-- Clinic Booking System - PostgreSQL Schema
-- Execute this script to set up the database schema

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

-- Create doctor_services junction table (Many-to-Many relationship)
CREATE TABLE IF NOT EXISTS doctor_services (
  doctor_id VARCHAR(50) NOT NULL,
  service_id VARCHAR(50) NOT NULL,
  PRIMARY KEY (doctor_id, service_id),
  FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
  FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
);

-- Create appointments table
CREATE TABLE IF NOT EXISTS appointments (
  id SERIAL PRIMARY KEY,
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
  FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE RESTRICT,
  FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE RESTRICT,
  UNIQUE(doctor_id, appointment_date, appointment_time)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor ON appointments(doctor_id);
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_name);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
CREATE INDEX IF NOT EXISTS idx_appointments_created_at ON appointments(created_at DESC);

-- Insert sample services
INSERT INTO services (id, name, duration, color) VALUES
  ('general', 'General Consultation', 30, '#2563eb'),
  ('cardio', 'Cardiology Review', 45, '#dc2626'),
  ('dental', 'Dental Checkup', 30, '#0891b2'),
  ('pediatric', 'Pediatric Visit', 30, '#16a34a')
ON CONFLICT (id) DO NOTHING;

-- Insert sample doctors
INSERT INTO doctors (id, name, specialty) VALUES
  ('amara', 'Dr. Amara Cole', 'Family Medicine'),
  ('levin', 'Dr. Rafael Levin', 'Cardiology'),
  ('noor', 'Dr. Noor Patel', 'Dentistry')
ON CONFLICT (id) DO NOTHING;

-- Insert doctor-service relationships
INSERT INTO doctor_services (doctor_id, service_id) VALUES
  ('amara', 'general'),
  ('amara', 'pediatric'),
  ('levin', 'general'),
  ('levin', 'cardio'),
  ('noor', 'dental')
ON CONFLICT (doctor_id, service_id) DO NOTHING;

-- Insert sample appointments
INSERT INTO appointments (patient_name, phone, email, service_id, doctor_id, appointment_date, appointment_time, status, notes) VALUES
  ('Maya Johnson', '+49 151 5550183', 'maya@gmail.com', 'general', 'amara', '2026-06-22', '09:00', 'Confirmed', 'Follow-up for blood pressure'),
  ('Daniel Smith', '+49 172 3234577', 'daniel@gmail.com', 'cardio', 'levin', '2026-06-22', '11:30', 'Pending', 'Chest discomfort review'),
  ('Ava Brown', '+49 170 5550144', 'ava@gmail.com', 'dental', 'noor', '2026-06-23', '10:00', 'Confirmed', 'Routine cleaning')
ON CONFLICT (doctor_id, appointment_date, appointment_time) DO NOTHING;

-- View: Get appointments with related information
CREATE OR REPLACE VIEW appointments_view AS
SELECT 
  a.id,
  a.patient_name,
  a.phone,
  a.email,
  a.appointment_date,
  a.appointment_time,
  a.status,
  a.notes,
  a.created_at,
  a.updated_at,
  s.name as service_name,
  s.duration,
  d.name as doctor_name,
  d.specialty
FROM appointments a
JOIN services s ON a.service_id = s.id
JOIN doctors d ON a.doctor_id = d.id;

-- Procedure: Get available time slots for a doctor on a specific date
CREATE OR REPLACE FUNCTION get_available_slots(
  doctor_id VARCHAR,
  appointment_date DATE,
  time_slots TEXT[]
) RETURNS TEXT[] AS $$
DECLARE
  booked_slots TEXT[];
  available_slots TEXT[];
  slot TEXT;
BEGIN
  -- Get booked slots for the doctor on that date
  SELECT ARRAY_AGG(appointment_time::TEXT) INTO booked_slots
  FROM appointments
  WHERE doctor_id = $1 
    AND appointment_date = $2 
    AND status != 'Cancelled';

  -- Filter out booked slots
  available_slots := ARRAY[]::TEXT[];
  FOREACH slot IN ARRAY $3 LOOP
    IF NOT (slot = ANY(booked_slots)) THEN
      available_slots := array_append(available_slots, slot);
    END IF;
  END LOOP;

  RETURN available_slots;
END;
$$ LANGUAGE plpgsql;

-- Procedure: Cancel appointment and log cancellation
CREATE OR REPLACE FUNCTION cancel_appointment(appointment_id INTEGER, cancellation_notes TEXT DEFAULT NULL)
RETURNS TABLE(success BOOLEAN, message TEXT) AS $$
DECLARE
  v_appointment_id INTEGER;
BEGIN
  v_appointment_id := $1;
  
  -- Check if appointment exists
  IF NOT EXISTS(SELECT 1 FROM appointments WHERE id = v_appointment_id) THEN
    RETURN QUERY SELECT false, 'Appointment not found'::TEXT;
    RETURN;
  END IF;

  -- Update appointment to cancelled
  UPDATE appointments
  SET status = 'Cancelled',
      notes = COALESCE(notes || ' | Cancelled: ' || cancellation_notes, 'Cancelled: ' || cancellation_notes),
      updated_at = NOW()
  WHERE id = v_appointment_id;

  RETURN QUERY SELECT true, 'Appointment cancelled successfully'::TEXT;
END;
$$ LANGUAGE plpgsql;

-- Procedure: Get appointment statistics
CREATE OR REPLACE FUNCTION get_appointment_stats(start_date DATE DEFAULT CURRENT_DATE, end_date DATE DEFAULT CURRENT_DATE + INTERVAL '30 days')
RETURNS TABLE(
  total_appointments BIGINT,
  confirmed_appointments BIGINT,
  pending_appointments BIGINT,
  cancelled_appointments BIGINT,
  doctor_name VARCHAR,
  doctor_appointment_count BIGINT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    COUNT(*) FILTER (WHERE appointment_date BETWEEN start_date AND end_date) as total_appointments,
    COUNT(*) FILTER (WHERE status = 'Confirmed' AND appointment_date BETWEEN start_date AND end_date) as confirmed_appointments,
    COUNT(*) FILTER (WHERE status = 'Pending' AND appointment_date BETWEEN start_date AND end_date) as pending_appointments,
    COUNT(*) FILTER (WHERE status = 'Cancelled' AND appointment_date BETWEEN start_date AND end_date) as cancelled_appointments,
    d.name,
    COUNT(*) FILTER (WHERE d.id = a.doctor_id AND appointment_date BETWEEN start_date AND end_date) as doctor_appointment_count
  FROM appointments a
  FULL OUTER JOIN doctors d ON a.doctor_id = d.id
  GROUP BY d.id, d.name;
END;
$$ LANGUAGE plpgsql;
