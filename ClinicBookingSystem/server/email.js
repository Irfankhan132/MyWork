require('dotenv').config();
const nodemailer = require('nodemailer');

const SMTP_HOST = process.env.SMTP_HOST;
const SMTP_PORT = process.env.SMTP_PORT ? Number(process.env.SMTP_PORT) : undefined;
const SMTP_USER = process.env.SMTP_USER;
const SMTP_PASS = process.env.SMTP_PASS;
const SMTP_SECURE = process.env.SMTP_SECURE === 'true';

let transporter = null;
if (SMTP_HOST && SMTP_PORT && SMTP_USER && SMTP_PASS) {
  transporter = nodemailer.createTransport({
    host: SMTP_HOST,
    port: SMTP_PORT,
    secure: SMTP_SECURE || SMTP_PORT === 465,
    auth: {
      user: SMTP_USER,
      pass: SMTP_PASS,
    },
  });
} else {
  console.warn('SMTP not configured; emails will not be sent. Set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS in .env');
}

async function sendAppointmentConfirmation(appointment) {
  if (!transporter) {
    console.log('Skipping email (no transporter) for', appointment.email);
    return;
  }

  const date = appointment.appointment_date ? String(appointment.appointment_date).slice(0, 10) : '';
  const time = appointment.appointment_time ? String(appointment.appointment_time).slice(0, 5) : '';
  const subject = `Appointment Confirmation — ${appointment.patient_name}`;
  const html = `
    <p>Dear ${appointment.patient_name},</p>
    <p>Your appointment has been booked:</p>
    <ul>
      <li><strong>Date:</strong> ${date}</li>
      <li><strong>Time:</strong> ${time}</li>
      <li><strong>Doctor:</strong> ${appointment.doctor_name || appointment.doctor_id}</li>
      <li><strong>Service:</strong> ${appointment.service_name || appointment.service_id}</li>
      <li><strong>Patient ID:</strong> ${appointment.patient_id || 'N/A'}</li>
    </ul>
    <p>Notes: ${appointment.notes || '—'}</p>
    <p>Thank you,<br/>Clinic</p>
  `;
  const text = `Dear ${appointment.patient_name},\n\nYour appointment has been booked:\nDate: ${date}\nTime: ${time}\nDoctor: ${appointment.doctor_name || appointment.doctor_id}\nService: ${appointment.service_name || appointment.service_id}\nPatient ID: ${appointment.patient_id || 'N/A'}\n\nNotes: ${appointment.notes || '-'}\n\nThank you,\nClinic`;

  const mailOptions = {
    from: process.env.SMTP_FROM || SMTP_USER,
    to: appointment.email,
    subject,
    text,
    html,
  };

  try {
    const info = await transporter.sendMail(mailOptions);
    console.log(`Email sent to ${appointment.email}: ${info.messageId}`);
    return info;
  } catch (err) {
    console.error('Error sending email to', appointment.email, err);
    throw err;
  }
}

module.exports = { sendAppointmentConfirmation };
