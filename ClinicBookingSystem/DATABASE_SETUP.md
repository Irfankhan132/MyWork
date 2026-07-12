# Clinic Booking System - Backend Setup Guide

## Database Setup

### 1. Install PostgreSQL
- **Windows**: Download from https://www.postgresql.org/download/windows/
- **Mac**: `brew install postgresql@15`
- **Linux**: `sudo apt-get install postgresql postgresql-contrib`

### 2. Create Database

Start PostgreSQL and run these commands:

```sql
-- Create database
CREATE DATABASE clinic_booking_db;

-- Connect to the database
\c clinic_booking_db
```

Or use psql command line:

```bash
psql -U postgres -c "CREATE DATABASE clinic_booking_db;"
```

### 3. Environment Configuration

Copy `.env.example` to `.env` and update with your PostgreSQL credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=clinic_booking_db
PORT=5000
```

## Installation & Running

### Install Dependencies
```bash
npm install
```

### Start Backend Server
```bash
npm run dev:server
```

Server will run on `http://localhost:5000`

### Start Frontend (separate terminal)
```bash
npm run dev
```

Frontend will run on `http://localhost:5173`

### Run Both Simultaneously (if concurrently is installed)
```bash
npm run dev:all
```

## API Endpoints

### Get All Appointments
```
GET /api/appointments
```

### Get Appointments by Date
```
GET /api/appointments/date/:date
```
Example: `/api/appointments/date/2026-06-22`

### Get Booked Slots for Doctor
```
GET /api/appointments/booked-slots/:doctorId/:date
```
Example: `/api/appointments/booked-slots/amara/2026-06-22`

### Create Appointment
```
POST /api/appointments
Content-Type: application/json

{
  "patient_name": "John Doe",
  "phone": "+49 123 456789",
  "email": "john@example.com",
  "service_id": "general",
  "doctor_id": "amara",
  "appointment_date": "2026-06-25",
  "appointment_time": "10:00",
  "notes": "Initial consultation"
}
```

### Update Appointment
```
PUT /api/appointments/:id
Content-Type: application/json

{
  "status": "Confirmed",
  "notes": "Updated notes"
}
```

Valid statuses: `Pending`, `Confirmed`, `Cancelled`, `Completed`

### Delete Appointment
```
DELETE /api/appointments/:id
```

### Search Appointments
```
GET /api/appointments/search/:query
```
Example: `/api/appointments/search/john`

## Database Schema

### Services Table
```
id (VARCHAR 50) - Primary Key
name (VARCHAR 255)
duration (INTEGER) - in minutes
color (VARCHAR 7) - hex color
```

### Doctors Table
```
id (VARCHAR 50) - Primary Key
name (VARCHAR 255)
specialty (VARCHAR 255)
```

### Doctor_Services (Junction Table)
```
doctor_id (VARCHAR 50) - Foreign Key
service_id (VARCHAR 50) - Foreign Key
```

### Appointments Table
```
id (SERIAL) - Primary Key
patient_name (VARCHAR 255)
phone (VARCHAR 20)
email (VARCHAR 255)
service_id (VARCHAR 50) - Foreign Key
doctor_id (VARCHAR 50) - Foreign Key
appointment_date (DATE)
appointment_time (TIME)
status (VARCHAR 50) - Pending, Confirmed, Cancelled, Completed
notes (TEXT)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
```

## Testing with cURL

```bash
# Create appointment
curl -X POST http://localhost:5000/api/appointments \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "John Doe",
    "phone": "+49 123 456789",
    "email": "john@example.com",
    "service_id": "general",
    "doctor_id": "amara",
    "appointment_date": "2026-06-25",
    "appointment_time": "14:00",
    "notes": "First visit"
  }'

# Get all appointments
curl http://localhost:5000/api/appointments

# Get appointments for a specific date
curl http://localhost:5000/api/appointments/date/2026-06-22

# Update appointment
curl -X PUT http://localhost:5000/api/appointments/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "Confirmed"}'
```

## Troubleshooting

### Connection refused error
- Ensure PostgreSQL is running
- Check database credentials in `.env`
- Verify database exists: `psql -U postgres -l`

### Unique constraint violation
- This means a doctor already has an appointment at that time
- The API returns 400 error: "This time slot is already booked"

### Tables already exist
- The server will not recreate tables if they already exist
- To reset: drop and recreate the database

## Frontend Integration

Update your React frontend to use the API endpoints instead of in-memory data. Example with axios:

```javascript
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

// Fetch appointments
const fetchAppointments = async () => {
  try {
    const response = await axios.get(`${API_URL}/appointments`);
    return response.data;
  } catch (error) {
    console.error('Error fetching appointments:', error);
  }
};

// Create appointment
const createAppointment = async (appointmentData) => {
  try {
    const response = await axios.post(`${API_URL}/appointments`, appointmentData);
    return response.data;
  } catch (error) {
    console.error('Error creating appointment:', error);
    throw error;
  }
};
```

## Production Checklist

- [ ] Update environment variables for production database
- [ ] Set `NODE_ENV=production`
- [ ] Enable HTTPS in production
- [ ] Add authentication and authorization
- [ ] Add input validation and sanitization
- [ ] Implement rate limiting
- [ ] Add database backups
- [ ] Set up monitoring and logging
- [ ] Use environment-specific configuration
- [ ] Add API documentation (Swagger/OpenAPI)
