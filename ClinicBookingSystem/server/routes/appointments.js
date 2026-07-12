const express = require('express');
const router = express.Router();
const pool = require('../db');
const emailer = require('../email');

const ADMIN_TOKEN = process.env.ADMIN_TOKEN || 'admin-secret-token';

async function generateUniquePatientId() {
  while (true) {
    const patientId = String(Math.floor(100000 + Math.random() * 900000));
    const { rows } = await pool.query('SELECT 1 FROM appointments WHERE patient_id = $1', [patientId]);
    if (rows.length === 0) {
      return patientId;
    }
  }
}

async function assignPatientIdIfMissing(row) {
  if (row.patient_id) {
    return row;
  }

  const existing = await pool.query(
    `SELECT patient_id FROM appointments WHERE email = $1 AND patient_id IS NOT NULL LIMIT 1`,
    [row.email]
  );

  let patientId = existing.rows[0]?.patient_id;
  if (!patientId) {
    patientId = await generateUniquePatientId();
  }

  await pool.query(`UPDATE appointments SET patient_id = $1 WHERE id = $2`, [patientId, row.id]);
  row.patient_id = patientId;
  return row;
}

function requireAdmin(req, res, next) {
  const authHeader = req.headers.authorization || '';
  const token = authHeader.replace(/^Bearer\s+/i, '');
  if (token === ADMIN_TOKEN) {
    return next();
  }
  return res.status(401).json({ error: 'Unauthorized' });
}

// Get all appointments (admin only)
router.get('/', requireAdmin, async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT a.id, a.patient_id, a.patient_name, a.phone, a.email, a.service_id, a.doctor_id, 
              a.appointment_date::text AS appointment_date, a.appointment_time::text AS appointment_time, 
              a.status, a.notes, d.name as doctor_name, d.specialty, s.name as service_name, s.duration 
       FROM appointments a 
       JOIN doctors d ON a.doctor_id = d.id 
       JOIN services s ON a.service_id = s.id 
       ORDER BY a.appointment_date DESC, a.appointment_time ASC`
    );
    const rows = await Promise.all(result.rows.map(assignPatientIdIfMissing));
    res.json(rows);
  } catch (error) {
    console.error('Error fetching appointments:', error);
    res.status(500).json({ error: 'Failed to fetch appointments' });
  }
});

// Get appointments by date
router.get('/date/:date', async (req, res) => {
  try {
    const { date } = req.params;
    const result = await pool.query(
      `SELECT a.id, a.patient_id, a.patient_name, a.phone, a.email, a.service_id, a.doctor_id,
              a.appointment_date::text AS appointment_date, a.appointment_time::text AS appointment_time,
              a.status, a.notes, d.name as doctor_name, d.specialty, s.name as service_name, s.duration
       FROM appointments a
       JOIN doctors d ON a.doctor_id = d.id
       JOIN services s ON a.service_id = s.id
       WHERE a.appointment_date = $1
       ORDER BY a.appointment_time ASC`,
      [date]
    );
    const rows = await Promise.all(result.rows.map(assignPatientIdIfMissing));
    res.json(rows);
  } catch (error) {
    console.error('Error fetching appointments by date:', error);
    res.status(500).json({ error: 'Failed to fetch appointments' });
  }
});

// Get booked time slots for a specific doctor on a specific date
router.get('/booked-slots/:doctorId/:date', async (req, res) => {
  try {
    const { doctorId, date } = req.params;
    const result = await pool.query(
      `SELECT appointment_time FROM appointments 
       WHERE doctor_id = $1 AND appointment_date = $2 AND status != 'Cancelled'`,
      [doctorId, date]
    );
    const bookedSlots = result.rows.map(row => row.appointment_time);
    res.json({ bookedSlots });
  } catch (error) {
    console.error('Error fetching booked slots:', error);
    res.status(500).json({ error: 'Failed to fetch booked slots' });
  }
});

// Create new appointment
router.post('/', async (req, res) => {
  const { patient_name, phone, email, service_id, doctor_id, appointment_date, appointment_time, notes } = req.body;

  // Validation
  if (!patient_name || !phone || !email || !service_id || !doctor_id || !appointment_date || !appointment_time) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  try {
    // Check if slot is already booked
    const checkSlot = await pool.query(
      `SELECT id FROM appointments 
       WHERE doctor_id = $1 AND appointment_date = $2 AND appointment_time = $3 AND status != 'Cancelled'`,
      [doctor_id, appointment_date, appointment_time]
    );

    if (checkSlot.rows.length > 0) {
      return res.status(400).json({ error: 'This time slot is already booked' });
    }

    let patientId;
    const existingPatient = await pool.query(`SELECT patient_id FROM appointments WHERE email = $1 AND patient_id IS NOT NULL LIMIT 1`, [email]);
    if (existingPatient.rows.length > 0) {
      patientId = existingPatient.rows[0].patient_id;
    } else {
      patientId = await generateUniquePatientId();
    }

    const result = await pool.query(
      `INSERT INTO appointments (patient_id, patient_name, phone, email, service_id, doctor_id, appointment_date, appointment_time, status, notes, created_at)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW())
       RETURNING id`,
      [patientId, patient_name, phone, email, service_id, doctor_id, appointment_date, appointment_time, 'Pending', notes || '']
    );

    const createdAppointment = await pool.query(
      `SELECT a.id, a.patient_id, a.patient_name, a.phone, a.email, a.service_id, a.doctor_id,
              a.appointment_date::text AS appointment_date, a.appointment_time::text AS appointment_time,
              a.status, a.notes
       FROM appointments a
       WHERE a.id = $1`,
      [result.rows[0].id]
    );

    const appointmentRow = createdAppointment.rows[0];
    const appointmentWithId = await assignPatientIdIfMissing(appointmentRow);

    // Try sending a confirmation email to the patient (fire-and-forget)
    emailer.sendAppointmentConfirmation(appointmentWithId).catch((err) => {
      console.error('Failed to send appointment confirmation email:', err);
    });

    res.status(201).json(appointmentWithId);
  } catch (error) {
    console.error('Error creating appointment:', error);
    res.status(500).json({ error: 'Failed to create appointment' });
  }
});

// Update appointment status
router.put('/:id', requireAdmin, async (req, res) => {
  const { id } = req.params;
  const { status, notes, appointment_date, appointment_time } = req.body;

  try {
    // fetch existing appointment to get doctor_id for conflict checks
    const existing = await pool.query('SELECT * FROM appointments WHERE id = $1', [id]);
    if (existing.rows.length === 0) {
      return res.status(404).json({ error: 'Appointment not found' });
    }
    const current = existing.rows[0];

    const updates = [];
    const params = [];
    let idx = 1;

    if (typeof status !== 'undefined') {
      const validStatuses = ['Pending', 'Confirmed', 'Cancelled', 'Completed'];
      if (!validStatuses.includes(status)) {
        return res.status(400).json({ error: 'Invalid status' });
      }
      updates.push(`status = $${idx++}`);
      params.push(status);
    }

    if (typeof notes !== 'undefined') {
      updates.push(`notes = $${idx++}`);
      params.push(notes);
    }

    if (typeof appointment_date !== 'undefined' && typeof appointment_time !== 'undefined') {
      // check for slot conflict with same doctor (exclude current id)
      const conflict = await pool.query(
        `SELECT id FROM appointments WHERE doctor_id = $1 AND appointment_date = $2 AND appointment_time = $3 AND id <> $4 AND status != 'Cancelled'`,
        [current.doctor_id, appointment_date, appointment_time, id]
      );
      if (conflict.rows.length > 0) {
        return res.status(400).json({ error: 'This time slot is already booked for the selected doctor' });
      }
      updates.push(`appointment_date = $${idx++}`);
      params.push(appointment_date);
      updates.push(`appointment_time = $${idx++}`);
      params.push(appointment_time);
    } else if (typeof appointment_date !== 'undefined' || typeof appointment_time !== 'undefined') {
      // if only one provided, refuse to partial update of slot
      return res.status(400).json({ error: 'Both appointment_date and appointment_time are required to change the slot' });
    }

    if (updates.length === 0) {
      return res.status(400).json({ error: 'No valid fields to update' });
    }

    // always set updated_at
    updates.push(`updated_at = NOW()`);

    const sql = `UPDATE appointments SET ${updates.join(', ')} WHERE id = $${idx} RETURNING *`;
    params.push(id);

    const result = await pool.query(sql, params);

    res.json(result.rows[0]);
  } catch (error) {
    console.error('Error updating appointment:', error);
    res.status(500).json({ error: 'Failed to update appointment' });
  }
});

// Delete appointment
router.delete('/:id', requireAdmin, async (req, res) => {
  const { id } = req.params;

  try {
    const result = await pool.query(
      `DELETE FROM appointments WHERE id = $1 RETURNING *`,
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'Appointment not found' });
    }

    res.json({ message: 'Appointment deleted successfully' });
  } catch (error) {
    console.error('Error deleting appointment:', error);
    res.status(500).json({ error: 'Failed to delete appointment' });
  }
});

// Search appointments by patient name
router.get('/search/:query', async (req, res) => {
  try {
    const { query } = req.params;
    const searchQuery = `%${query}%`;
    const result = await pool.query(
      `SELECT a.*, d.name as doctor_name, d.specialty, s.name as service_name 
       FROM appointments a 
       JOIN doctors d ON a.doctor_id = d.id 
       JOIN services s ON a.service_id = s.id 
       WHERE LOWER(a.patient_name) LIKE LOWER($1)
         OR LOWER(a.email) LIKE LOWER($1)
         OR a.patient_id = $2
       ORDER BY a.appointment_date DESC, a.appointment_time ASC`,
      [searchQuery, query]
    );
    const rows = await Promise.all(result.rows.map(assignPatientIdIfMissing));
    res.json(rows);
  } catch (error) {
    console.error('Error searching appointments:', error);
    res.status(500).json({ error: 'Failed to search appointments' });
  }
});

module.exports = router;
