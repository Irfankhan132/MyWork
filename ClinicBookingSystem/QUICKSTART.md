# Quick Start - PostgreSQL Backend Setup

## Prerequisites
- Node.js (v14+) installed
- PostgreSQL (v12+) installed and running

## Step 1: Create Database
```bash
# Login to PostgreSQL
psql -U postgres

# Run this command
CREATE DATABASE clinic_booking_db;

# Exit psql
\q
```

## Step 2: Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your PostgreSQL credentials
```

## Step 3: Install Dependencies
```bash
npm install
```

## Step 4: Run the Server
```bash
# Terminal 1 - Backend
npm run dev:server

# Terminal 2 - Frontend
npm run dev
```

Or run both simultaneously:
```bash
npm run dev:all
```

## Step 5: Test the API
Visit in your browser:
- Frontend: `http://localhost:5173`
- Backend Health: `http://localhost:5000/api/health`
- API: `http://localhost:5000/api/appointments`

## Database Created with:
- ✅ **Services Table** - Medical services (General, Cardiology, Dental, Pediatric)
- ✅ **Doctors Table** - Doctor information (Dr. Amara Cole, Dr. Rafael Levin, Dr. Noor Patel)
- ✅ **Doctor-Services Junction** - Link doctors to their services
- ✅ **Appointments Table** - Patient appointments with validation
- ✅ **Indexes** - For optimized queries
- ✅ **Sample Data** - Pre-loaded with example records

## What's New:
- `server/server.js` - Express backend server
- `server/db.js` - PostgreSQL connection
- `server/routes/appointments.js` - API endpoints
- `src/api/appointmentAPI.js` - Frontend API helper functions
- `database/schema.sql` - Full database schema
- `DATABASE_SETUP.md` - Detailed setup guide
- `.env.example` - Environment variables template
- `.gitignore` - Git ignore file
- Updated `package.json` - Backend dependencies

## API Endpoints Summary:
- `POST /api/appointments` - Create appointment
- `GET /api/appointments` - Get all appointments
- `GET /api/appointments/date/:date` - Get appointments by date
- `GET /api/appointments/booked-slots/:doctorId/:date` - Get booked slots
- `PUT /api/appointments/:id` - Update appointment
- `DELETE /api/appointments/:id` - Delete appointment
- `GET /api/appointments/search/:query` - Search appointments

## Troubleshooting:
- **PostgreSQL not running?** Start the service:
  - Windows: `pg_ctl -D "C:\Program Files\PostgreSQL\data" start`
  - Mac: `brew services start postgresql`
  - Linux: `sudo systemctl start postgresql`

- **Port already in use?** Change PORT in .env (default: 5000)

- **Database doesn't exist?** The server auto-creates tables on first run

For more details, see `DATABASE_SETUP.md`
