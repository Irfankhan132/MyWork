const express = require('express');
const cors = require('cors');
require('dotenv').config();
const pool = require('./db');

const appointmentsRouter = require('./routes/appointments');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'Server is running' });
});

// Routes
app.use('/api/appointments', appointmentsRouter);

app.post('/api/admin/login', (req, res) => {
  const { username, password } = req.body;
  const adminUser = process.env.ADMIN_USER || 'admin';
  const adminPassword = process.env.ADMIN_PASSWORD || 'admin123';
  const adminToken = process.env.ADMIN_TOKEN || 'admin-secret-token';

  if (username === adminUser && password === adminPassword) {
    return res.json({ token: adminToken });
  }

  return res.status(401).json({ error: 'Invalid admin credentials' });
});

// Initialize database and seed data
async function initializeDatabase() {
  try {
    console.log('Checking database connection...');
    await pool.query('SELECT NOW()');
    console.log('✓ Database connection successful');

    // Check if tables exist
    const tablesCheck = await pool.query(
      `SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name = 'doctors')`
    );

    if (!tablesCheck.rows[0].exists) {
      console.log('Creating database schema...');
      await createSchema();
      console.log('✓ Database schema created');
    } else {
      console.log('✓ Database schema already exists');
    }

    await ensurePatientIdColumn();
    await populateMissingPatientIds();
  } catch (error) {
    console.error('Database initialization error:', error);
    process.exit(1);
  }
}

async function createSchema() {
  const schema = `
    -- Create services table
    CREATE TABLE IF NOT EXISTS services (
      id VARCHAR(50) PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      duration INTEGER NOT NULL,
      color VARCHAR(7)
    );

    -- Create doctors table
    CREATE TABLE IF NOT EXISTS doctors (
      id VARCHAR(50) PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      specialty VARCHAR(255) NOT NULL
    );

    -- Create doctor_services junction table
    CREATE TABLE IF NOT EXISTS doctor_services (
      doctor_id VARCHAR(50) NOT NULL,
      service_id VARCHAR(50) NOT NULL,
      PRIMARY KEY (doctor_id, service_id),
      FOREIGN KEY (doctor_id) REFERENCES doctors(id),
      FOREIGN KEY (service_id) REFERENCES services(id)
    );

    -- Create appointments table
    CREATE TABLE IF NOT EXISTS appointments (
      id SERIAL PRIMARY KEY,
      patient_id VARCHAR(6),
      patient_name VARCHAR(255) NOT NULL,
      phone VARCHAR(20) NOT NULL,
      email VARCHAR(255) NOT NULL,
      service_id VARCHAR(50) NOT NULL,
      doctor_id VARCHAR(50) NOT NULL,
      appointment_date DATE NOT NULL,
      appointment_time TIME NOT NULL,
      status VARCHAR(50) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Confirmed', 'Cancelled', 'Completed')),
      notes TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (service_id) REFERENCES services(id),
      FOREIGN KEY (doctor_id) REFERENCES doctors(id),
      UNIQUE(doctor_id, appointment_date, appointment_time)
    );

    -- Create indexes for better query performance
    CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);
    CREATE INDEX IF NOT EXISTS idx_appointments_doctor ON appointments(doctor_id);
    CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_name);
    CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
    CREATE INDEX IF NOT EXISTS idx_appointments_patient_id ON appointments(patient_id);

    -- Insert sample data
    INSERT INTO services (id, name, duration, color) VALUES
      ('general', 'General Consultation', 30, '#2563eb'),
      ('cardio', 'Cardiology Review', 45, '#dc2626'),
      ('dental', 'Dental Checkup', 30, '#0891b2'),
      ('pediatric', 'Pediatric Visit', 30, '#16a34a')
    ON CONFLICT (id) DO NOTHING;

    INSERT INTO doctors (id, name, specialty) VALUES
      ('amara', 'Dr. Amara Cole', 'Family Medicine'),
      ('levin', 'Dr. Rafael Levin', 'Cardiology'),
      ('noor', 'Dr. Noor Patel', 'Dentistry')
    ON CONFLICT (id) DO NOTHING;

    INSERT INTO doctor_services (doctor_id, service_id) VALUES
      ('amara', 'general'),
      ('amara', 'pediatric'),
      ('levin', 'general'),
      ('levin', 'cardio'),
      ('noor', 'dental')
    ON CONFLICT (doctor_id, service_id) DO NOTHING;

    INSERT INTO appointments (patient_name, phone, email, service_id, doctor_id, appointment_date, appointment_time, status, notes) VALUES
      ('Maya Johnson', '+49 151 5550183', 'maya@gmail.com', 'general', 'amara', '2026-06-22', '09:00', 'Confirmed', 'Follow-up for blood pressure'),
      ('Daniel Smith', '+49 172 3234577', 'daniel@gmail.com', 'cardio', 'levin', '2026-06-22', '11:30', 'Pending', 'Chest discomfort review'),
      ('Ava Brown', '+49 170 5550144', 'ava@gmail.com', 'dental', 'noor', '2026-06-23', '10:00', 'Confirmed', 'Routine cleaning')
    ON CONFLICT (doctor_id, appointment_date, appointment_time) DO NOTHING;
  `;

  try {
    await pool.query(schema);
  } catch (error) {
    console.error('Error creating schema:', error);
    throw error;
  }
}

async function ensurePatientIdColumn() {
  try {
    await pool.query(`ALTER TABLE appointments DROP CONSTRAINT IF EXISTS appointments_patient_id_key`);
    await pool.query(`DROP INDEX IF EXISTS appointments_patient_id_key`);
    await pool.query(`ALTER TABLE appointments ADD COLUMN IF NOT EXISTS patient_id VARCHAR(6)`);
    await pool.query(`CREATE INDEX IF NOT EXISTS idx_appointments_patient_id ON appointments(patient_id)`);
  } catch (error) {
    console.error('Error ensuring patient_id column:', error);
    throw error;
  }
}

async function generateUniquePatientId() {
  while (true) {
    const patientId = String(Math.floor(100000 + Math.random() * 900000));
    const { rows } = await pool.query('SELECT 1 FROM appointments WHERE patient_id = $1', [patientId]);
    if (rows.length === 0) {
      return patientId;
    }
  }
}

async function populateMissingPatientIds() {
  try {
    const { rows } = await pool.query(`SELECT id, email FROM appointments WHERE patient_id IS NULL OR patient_id = ''`);
    for (const row of rows) {
      const { id, email } = row;
      const { rows: existing } = await pool.query(`SELECT patient_id FROM appointments WHERE email = $1 AND patient_id IS NOT NULL LIMIT 1`, [email]);
      let patientId = existing[0]?.patient_id;
      if (!patientId) {
        patientId = await generateUniquePatientId();
      }
      await pool.query(`UPDATE appointments SET patient_id = $1 WHERE id = $2`, [patientId, id]);
    }
  } catch (error) {
    console.error('Error populating missing patient IDs:', error);
    throw error;
  }
}

// Start server
initializeDatabase().then(() => {
  app.listen(PORT, () => {
    console.log(`\n🏥 Clinic Booking System Backend`);
    console.log(`✓ Server running on http://localhost:${PORT}`);
    console.log(`✓ API Health: http://localhost:${PORT}/api/health`);
    console.log(`✓ Appointments API: http://localhost:${PORT}/api/appointments\n`);
  });
}).catch((error) => {
  console.error('Failed to initialize database:', error);
  process.exit(1);
});

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\nShutting down gracefully...');
  await pool.end();
  process.exit(0);
});
