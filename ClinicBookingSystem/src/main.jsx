import React, { useMemo, useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import {
  CalendarDays,
  Check,
  Clock3,
  Filter,
  HeartPulse,
  Mail,
  Phone,
  Plus,
  Search,
  Stethoscope,
  UserRound,
  UsersRound
} from "lucide-react";
import "./styles.css";
import { appointmentAPI } from "./api/appointmentAPI";

const services = [
  { id: "general", name: "General Consultation", duration: 30, color: "#2563eb" },
  { id: "cardio", name: "Cardiology Review", duration: 45, color: "#dc2626" },
  { id: "dental", name: "Dental Checkup", duration: 30, color: "#0891b2" },
  { id: "pediatric", name: "Pediatric Visit", duration: 30, color: "#16a34a" }
];

const doctors = [
  { id: "amara", name: "Dr. Amara Cole", specialty: "Family Medicine", services: ["general", "pediatric"] },
  { id: "levin", name: "Dr. Rafael Levin", specialty: "Cardiology", services: ["general", "cardio"] },
  { id: "noor", name: "Dr. Noor Patel", specialty: "Dentistry", services: ["dental"] }
];

const timeSlots = ["08:30", "09:00", "09:30", "10:00", "10:30", "11:30", "13:00", "13:30", "14:00", "15:00", "16:00"];

const initialAppointments = [
  {
    id: 1,
    patient: "Maya Johnson",
    phone: "+49 151 5550183",
    email: "maya@gmail.com",
    serviceId: "general",
    doctorId: "amara",
    date: "2026-06-22",
    time: "09:00",
    status: "Confirmed",
    notes: "Follow-up for blood pressure"
  },
  {
    id: 2,
    patient: "Daniel Smith",
    phone: "+49 172 3234577",
    email: "daniel@gmail.com",
    serviceId: "cardio",
    doctorId: "levin",
    date: "2026-06-22",
    time: "11:30",
    status: "Pending",
    notes: "Chest discomfort review"
  },
  {
    id: 3,
    patient: "Ava Brown",
    phone: "+49 170 5550144",
    email: "ava@gmail.com",
    serviceId: "dental",
    doctorId: "noor",
    date: "2026-06-23",
    time: "10:00",
    status: "Confirmed",
    notes: "Routine cleaning"
  }
];

const today = toDateInputValue(new Date());
const earliestBookingDate = toDateInputValue(addDays(new Date(), 1));

function App() {
  const [appointments, setAppointments] = useState([]);
  const [selectedDate, setSelectedDate] = useState(earliestBookingDate);
  const [query, setQuery] = useState("");
  const [adminQuery, setAdminQuery] = useState("");
  const [adminDate, setAdminDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [validationError, setValidationError] = useState("");
  const [viewMode, setViewMode] = useState("user");
  const [isAdmin, setIsAdmin] = useState(false);
  const [adminUsername, setAdminUsername] = useState("");
  const [adminPassword, setAdminPassword] = useState("");
  const [adminError, setAdminError] = useState("");
  const [adminToken, setAdminToken] = useState("");
  const [form, setForm] = useState({
    patient: "",
    countryCode: "+49",
    phoneNumber: "",
    email: "",
    serviceId: "general",
    doctorId: "amara",
    date: earliestBookingDate,
    time: "08:30",
    notes: ""
  });

  const service = services.find((item) => item.id === form.serviceId);
  const availableDoctors = doctors.filter((doctor) => doctor.services.includes(form.serviceId));

  const filteredAppointments = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return appointments
      .filter((appointment) => {
        if (!normalized) return true;
        const doctor = doctors.find((item) => item.id === appointment.doctorId);
        const appointmentService = services.find((item) => item.id === appointment.serviceId);
        return [appointment.patient, appointment.patientId, doctor?.name, appointmentService?.name, appointment.status]
          .join(" ")
          .toLowerCase()
          .includes(normalized);
      })
      .sort((a, b) => a.time.localeCompare(b.time));
  }, [appointments, query]);

  const availableTimeSlots = getAvailableTimeSlots(form.date, appointments);
  const hasAvailableTimeSlots = availableTimeSlots.length > 0;

  const stats = {
    today: appointments.filter((appointment) => appointment.date === today).length,
    confirmed: appointments.filter((appointment) => appointment.status === "Confirmed").length,
    pending: appointments.filter((appointment) => appointment.status === "Pending").length,
    patients: new Set(appointments.map((appointment) => appointment.patient)).size
  };

  function updateField(field, value) {
    setValidationError("");
    setForm((current) => {
      const next = { ...current, [field]: value };
      if (field === "serviceId") {
        const firstDoctor = doctors.find((doctor) => doctor.services.includes(value));
        next.doctorId = firstDoctor?.id ?? "";
      }
      if (field === "date") {
        const dateSlots = getAvailableTimeSlots(value, appointments);
        next.time = dateSlots.includes(current.time) ? current.time : dateSlots[0] ?? "";
      }
      return next;
    });
  }

  function bookAppointment(event) {
    event.preventDefault();
    const error = getBookingError(form, appointments);
    if (error) {
      setValidationError(error);
      return;
    }
    const cleanPhone = formatPhone(form.countryCode, form.phoneNumber);
    (async () => {
      try {
        const payload = {
          patient: form.patient.trim(),
          phone: cleanPhone,
          email: form.email,
          serviceId: form.serviceId,
          doctorId: form.doctorId,
          date: form.date,
          time: form.time,
          notes: form.notes
        };
        const created = await appointmentAPI.create(payload);

        const mapped = mapServerToClient(created);
        const nextAppointments = [...appointments, mapped];
        setAppointments(nextAppointments);

        setSelectedDate(form.date);
        setForm((current) => ({
          ...current,
          patient: "",
          // keep selected country code but clear local number and email
          phoneNumber: "",
          email: "",
          notes: "",
          time: getAvailableTimeSlots(current.date, nextAppointments)[0] ?? ""
        }));
      } catch (err) {
        setValidationError(err.message || 'Failed to create appointment');
      }
    })();
  }

  async function toggleStatus(id) {
    const current = appointments.find((a) => a.id === id);
    if (!current) return;
    const newStatus = current.status === "Confirmed" ? "Pending" : "Confirmed";
    try {
      const updated = await appointmentAPI.update(id, { status: newStatus });
      setAppointments((list) => list.map((a) => (a.id === id ? mapServerToClient(updated) : a)));
    } catch (err) {
      console.error('Failed to update status', err);
    }
  }

  function convertToIsoDate(value) {
    const trimmed = value.trim();
    if (/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) {
      return trimmed;
    }
    if (/^\d{2}\.\d{2}\.\d{4}$/.test(trimmed)) {
      const [d, m, y] = trimmed.split('.');
      return `${y}-${m}-${d}`;
    }
    if (/^\d{2}\/\d{2}\/\d{4}$/.test(trimmed)) {
      const [m, d, y] = trimmed.split('/');
      return `${y}-${m}-${d}`;
    }
    return null;
  }

  async function loadAppointmentsByDate(date) {
    setLoading(true);
    try {
      const rows = await appointmentAPI.getByDate(date);
      setAppointments(rows.map(mapServerToClient));
    } catch (err) {
      console.warn('Failed to load appointments by date:', err.message || err);
      setAppointments([]);
    } finally {
      setLoading(false);
    }
  }

  async function loadAllAppointments(token) {
    setLoading(true);
    try {
      const rows = await appointmentAPI.getAll(token);
      setAppointments(rows.map(mapServerToClient));
    } catch (err) {
      console.warn('Failed to load all appointments:', err.message || err);
      setAppointments([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleAdminLogin() {
    setAdminError("");
    try {
      const result = await appointmentAPI.login({ username: adminUsername, password: adminPassword });
      setAdminToken(result.token);
      setIsAdmin(true);
      setViewMode('admin');
      setAdminError("");
      await loadAllAppointments(result.token);
    } catch (err) {
      setAdminError(err.message || 'Invalid admin credentials');
      setIsAdmin(false);
      setAdminToken("");
    }
  }

  function handleAdminLogout() {
    setIsAdmin(false);
    setAdminToken("");
    setAdminUsername("");
    setAdminPassword("");
    setAdminError("");
    setAdminQuery("");
    setAdminDate("");
    setAppointments([]);
  }

  async function handleAdminSave(appointmentId, updates) {
    try {
      const updated = await appointmentAPI.update(appointmentId, updates, adminToken);
      setAppointments((list) => list.map((appointment) => (appointment.id === appointmentId ? mapServerToClient(updated) : appointment)));
    } catch (err) {
      console.error('Failed to save appointment update:', err);
    }
  }

  async function handleAdminUpdate(appointmentId, updates) {
    try {
      const updated = await appointmentAPI.update(appointmentId, updates, adminToken);
      setAppointments((list) => list.map((appointment) => (appointment.id === appointmentId ? mapServerToClient(updated) : appointment)));
    } catch (err) {
      console.error('Failed to update appointment date/time:', err);
    }
  }

  async function handleAdminDelete(id) {
    try {
      await appointmentAPI.delete(id, adminToken);
      setAppointments((list) => list.filter((appointment) => appointment.id !== id));
    } catch (err) {
      console.error('Failed to delete appointment:', err);
    }
  }

  async function searchAppointments(queryValue) {
    setLoading(true);
    try {
      const dateQuery = convertToIsoDate(queryValue);
      if (dateQuery) {
        await loadAppointmentsByDate(dateQuery);
      } else {
        const rows = await appointmentAPI.search(queryValue);
        setAppointments(rows.map(mapServerToClient));
      }
    } catch (err) {
      console.warn('Failed to search appointments:', err.message || err);
      setAppointments([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (viewMode === 'admin' && isAdmin) {
      if (adminQuery.trim()) {
        const timeout = setTimeout(() => {
          searchAppointments(adminQuery);
        }, 250);
        return () => clearTimeout(timeout);
      }

      if (adminDate) {
        loadAppointmentsByDate(adminDate);
        return;
      }

      loadAllAppointments(adminToken);
      return;
    }

    if (!query.trim()) {
      loadAppointmentsByDate(selectedDate);
      return;
    }

    const timeout = setTimeout(() => {
      searchAppointments(query);
    }, 250);

    return () => clearTimeout(timeout);
  }, [query, selectedDate, viewMode, isAdmin, adminToken, adminQuery, adminDate]);

  useEffect(() => {
    if (!query.trim() && viewMode === 'user') {
      loadAppointmentsByDate(selectedDate);
    }
  }, [selectedDate, query, viewMode]);

  return (
    <main className="app-shell">
      <aside className="sidebar" aria-label="Clinic navigation">
        <div className="brand">
          <span className="brand-mark"><HeartPulse size={22} /></span>
          <div>
            <strong>ClinicBook</strong>
            <small>Appointment desk</small>
          </div>
        </div>

        <nav className="nav-list">
          <a className="nav-item active" href="#booking"><CalendarDays size={18} />Booking</a>
          <a className="nav-item" href="#schedule"><Clock3 size={18} />Schedule</a>
          <a className="nav-item" href="#patients"><UsersRound size={18} />Patients</a>
          <a className="nav-item" href="#doctors"><Stethoscope size={18} />Doctors</a>
        </nav>

        <div className="clinic-card">
          <span>Open today</span>
          <strong>08:30 - 17:00</strong>
          <p>Front desk capacity is balanced across all active providers.</p>
        </div>
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <p className="eyebrow">Clinic Booking System</p>
            <h1>Book and manage patient appointments</h1>
          </div>
          <button className="primary-action" type="button" onClick={() => document.querySelector("#booking-form")?.scrollIntoView({ behavior: "smooth" })}>
            <Plus size={18} />New booking
          </button>
          <button className="secondary-action" type="button" onClick={() => setViewMode(viewMode === 'admin' ? 'user' : 'admin')}>
            {viewMode === 'admin' ? 'User View' : 'Admin View'}
          </button>
        </header>

        {viewMode === 'admin' ? (
          <section className="admin-panel">
            {!isAdmin ? (
              <div className="admin-login-panel">
                <div className="section-heading">
                  <div>
                    <p className="eyebrow">Admin login</p>
                    <h2>Administrator access</h2>
                  </div>
                </div>
                <div className="admin-login-form">
                  <label>
                    Username
                    <input value={adminUsername} onChange={(event) => setAdminUsername(event.target.value)} placeholder="admin" />
                  </label>
                  <label>
                    Password
                    <input type="password" value={adminPassword} onChange={(event) => setAdminPassword(event.target.value)} placeholder="admin123" />
                  </label>
                  {adminError && <p className="form-error">{adminError}</p>}
                  <button type="button" className="submit-button" onClick={handleAdminLogin}>Login as admin</button>
                </div>
              </div>
            ) : (
              <div className="admin-dashboard">
                <div className="section-heading">
                  <div>
                    <p className="eyebrow">Admin Dashboard</p>
                    <h2>All Appointments</h2>
                  </div>
                  <button className="secondary-action" type="button" onClick={handleAdminLogout}>Logout</button>
                </div>
                <section className="metrics admin-metrics" aria-label="Admin appointment summary">
                  <Metric icon={<UsersRound />} label="Booked" value={appointments.length} />
                  <Metric icon={<Clock3 />} label="Pending" value={appointments.filter((appointment) => appointment.status === 'Pending').length} />
                  <Metric icon={<Check />} label="Completed" value={appointments.filter((appointment) => appointment.status === 'Completed').length} />
                </section>
                <div className="search-row admin-controls">
                  <label className="search-field admin-search-field">
                    <input
                      value={adminQuery}
                      onChange={(event) => {
                        setAdminDate("");
                        setAdminQuery(event.target.value);
                      }}
                      placeholder="Search by patient name"
                    />
                  </label>
                  <label className="date-field admin-date-field">
                    <span>Date</span>
                    <input
                      type="date"
                      value={adminDate}
                      onChange={(event) => {
                        setAdminQuery("");
                        setAdminDate(event.target.value);
                      }}
                    />
                  </label>
                </div>
                {loading ? (
                  <div>Loading appointments...</div>
                ) : (
                  <div className="admin-appointment-table">
                    <div className="table-header">
                      <span>Patient</span>
                      <span>ID</span>
                      <span>Date</span>
                      <span>Time</span>
                      <span>Doctor</span>
                      <span>Service</span>
                      <span>Status</span>
                      <span>Notes</span>
                      <span>Actions</span>
                    </div>
                    {appointments.map((appointment) => (
                      <AdminRow
                        key={appointment.id}
                        appointment={appointment}
                        services={services}
                        doctors={doctors}
                        onSave={handleAdminSave}
                        onDelete={handleAdminDelete}
                      />
                    ))}
                  </div>
                )}
              </div>
            )}
          </section>
        ) : (
          <>
            <section className="workspace">
              <form className="booking-panel" id="booking-form" onSubmit={bookAppointment}>
                <div className="section-heading">
                  <div>
                    <p className="eyebrow">New appointment</p>
                    <h2>Patient details</h2>
                  </div>
                  <span className="duration">{service?.duration} min</span>
                </div>

                <label>
                  Patient name
                  <input value={form.patient} onChange={(event) => updateField("patient", event.target.value)} placeholder="Enter full name" />
                </label>

                <label>
                  Phone
                  <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                    <select
                      value={form.countryCode}
                      onChange={(event) => updateField('countryCode', event.target.value)}
                      style={{ width: 160, minWidth: 120 }}
                    >
                      <option value="+49">+49 Germany</option>
                      <option value="+39">+39 Italy</option>
                      <option value="+92">+92 Pakistan</option>
                      <option value="+1">+1 USA</option>
                      <option value="+44">+44 UK</option>
                    </select>
                    <input
                      type="tel"
                      value={form.phoneNumber}
                      onChange={(event) => updateField('phoneNumber', event.target.value)}
                      placeholder="Enter Phone Number"
                      style={{ flex: 1, minWidth: 140 }}
                    />
                  </div>
                </label>

                <label>
                  Email
                  <input
                    type="email"
                    value={form.email}
                    onChange={(event) => updateField("email", event.target.value)}
                    placeholder="xyz@gmail.com"
                    pattern="^[A-Za-z0-9._%+-]+@(gmail|yahoo)\.com$"
                    title="Use an email address like xyz@gmail.com or xyz@yahoo.com"
                  />
                </label>

                <label>
                  Service
                  <select value={form.serviceId} onChange={(event) => updateField("serviceId", event.target.value)}>
                    {services.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
                  </select>
                </label>

                <label>
                  Doctor
                  <select value={form.doctorId} onChange={(event) => updateField("doctorId", event.target.value)}>
                    {availableDoctors.map((doctor) => <option key={doctor.id} value={doctor.id}>{doctor.name} - {doctor.specialty}</option>)}
                  </select>
                </label>

                <div className="two-col">
                  <label>
                    Date
                    <input
                      type="date"
                      value={form.date}
                      min={earliestBookingDate}
                      onChange={(event) => updateField("date", event.target.value)}
                    />
                  </label>
                  <label>
                    Time
                    <select value={form.time} onChange={(event) => updateField("time", event.target.value)} disabled={!hasAvailableTimeSlots}>
                      {hasAvailableTimeSlots ? (
                        availableTimeSlots.map((slot) => <option key={slot} value={slot}>{slot}</option>)
                      ) : (
                        <option value="">No times available</option>
                      )}
                    </select>
                  </label>
                </div>

                <label>
                  Notes
                  <textarea value={form.notes} onChange={(event) => updateField("notes", event.target.value)} placeholder="Reason for visit, symptoms, or internal notes" />
                </label>

                {validationError && <p className="form-error">{validationError}</p>}

                <button className="submit-button" type="submit" disabled={!hasAvailableTimeSlots}>
                  <CalendarDays size={18} />Book appointment
                </button>
              </form>

              <section className="schedule-panel" id="schedule">
                <div className="section-heading">
                  <div>
                    <p className="eyebrow">Daily schedule</p>
                    <h2>{formatDate(selectedDate)}</h2>
                  </div>
                  <input className="date-filter" type="date" value={selectedDate} onChange={(event) => setSelectedDate(event.target.value)} />
                </div>

                <div className="search-row">
                  <label className="search-field">
                    <Search size={17} />
                    <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search by name, date, or patient ID" />
                  </label>
                  <button className="icon-button" type="button" title="Filter schedule" aria-label="Filter schedule">
                    <Filter size={18} />
                  </button>
                </div>

                <div className="appointment-list">
                  {filteredAppointments.length === 0 ? (
                    <div className="empty-state">No appointments match this day.</div>
                  ) : (
                    filteredAppointments.map((appointment) => (
                      <AppointmentCard key={appointment.id} appointment={appointment} onToggleStatus={toggleStatus} />
                    ))
                  )}
                </div>
              </section>
            </section>
          </>
        )}
      </section>
    </main>
  );
}

function Metric({ icon, label, value }) {
  return (
    <article className="metric">
      <span>{icon}</span>
      <div>
        <strong>{value}</strong>
        <small>{label}</small>
      </div>
    </article>
  );
}

function AppointmentCard({ appointment, onToggleStatus }) {
  const service = services.find((item) => item.id === appointment.serviceId);
  const doctor = doctors.find((item) => item.id === appointment.doctorId);

  return (
    <article className="appointment-card">
      <div className="time-column">
        <strong>{appointment.time}</strong>
        <span style={{ backgroundColor: service?.color }} />
      </div>
      <div className="appointment-body">
        <div className="appointment-title">
          <div>
            <h3>{appointment.patient}</h3>
            <p>Patient ID: <strong>{appointment.patientId || 'N/A'}</strong></p>
            <p>{service?.name} with {doctor?.name}</p>
          </div>
          <button className={`status ${appointment.status.toLowerCase()}`} type="button" onClick={() => onToggleStatus(appointment.id)}>
            {appointment.status}
          </button>
        </div>
        <div className="contact-row">
          <span><Phone size={15} />{appointment.phone}</span>
          <span><Mail size={15} />{appointment.email}</span>
        </div>
        {appointment.notes && <p className="notes">{appointment.notes}</p>}
      </div>
    </article>
  );
}

function AdminRow({ appointment, services, doctors, onSave, onDelete }) {
  const [localStatus, setLocalStatus] = useState(appointment.status);
  const [localNotes, setLocalNotes] = useState(appointment.notes || '');
  const [isEditing, setIsEditing] = useState(false);
  const doctor = doctors.find((item) => item.id === appointment.doctorId);
  const service = services.find((item) => item.id === appointment.serviceId);
  const statusOptions = ['Pending', 'Confirmed', 'Completed', 'Cancelled'];
  const [localDate, setLocalDate] = useState(appointment.date);
  const [localTime, setLocalTime] = useState(appointment.time);
  const timeSlots = [
    '08:30', '09:00', '09:30', '10:00', '10:30', '11:30', '13:00', '13:30', '14:00', '15:00', '16:00'
  ];

  return (
    <div className="table-row">
      <span>{appointment.patient}</span>
      <span>{appointment.patientId || '—'}</span>
      <span>{appointment.date}</span>
      <span>{appointment.time}</span>
      <span>{doctor?.name || appointment.doctorId}</span>
      <span>{service?.name || appointment.serviceId}</span>
      <span>
        <select value={localStatus} onChange={(event) => setLocalStatus(event.target.value)}>
          {statusOptions.map((status) => (
            <option key={status} value={status}>{status}</option>
          ))}
        </select>
      </span>
      <span>
        <input
          type="text"
          className="admin-row-notes"
          value={localNotes}
          onChange={(event) => setLocalNotes(event.target.value)}
          placeholder="Add notes"
        />
      </span>
      <span className="admin-row-actions">
        <button
          type="button"
          className="success-button"
          onClick={() => onSave(appointment.id, { status: localStatus, notes: localNotes })}
        >
          Save
        </button>
        <button
          type="button"
          className="primary-action admin-update-button"
          onClick={() => setIsEditing((current) => !current)}
        >
          {isEditing ? 'Close' : 'Update'}
        </button>
        <button
          type="button"
          className="danger-button"
          onClick={() => onDelete(appointment.id)}
        >
          Delete
        </button>
      </span>
      {isEditing && (
        <div className="admin-edit-panel">
          <label>
            Patient
            <input type="text" value={appointment.patient} disabled />
          </label>
          <label>
            Phone
            <input type="text" value={appointment.phone} disabled />
          </label>
          <label>
            Email
            <input type="text" value={appointment.email} disabled />
          </label>
          <label>
            Appointment date
            <input
              type="date"
              value={localDate}
              onChange={(event) => setLocalDate(event.target.value)}
              min={new Date().toISOString().slice(0, 10)}
            />
          </label>
          <label>
            Appointment time
            <select value={localTime} onChange={(event) => setLocalTime(event.target.value)}>
              {timeSlots.map((slot) => (
                <option key={slot} value={slot}>{slot}</option>
              ))}
            </select>
          </label>
          <button
            type="button"
            className="primary-action admin-apply-button"
            onClick={() => {
              onSave(appointment.id, {
                status: localStatus,
                notes: localNotes,
                date: localDate,
                time: localTime
              });
              setIsEditing(false);
            }}
          >
            Apply date/time
          </button>
        </div>
      )}
    </div>
  );
}

function formatDate(value) {
  return new Intl.DateTimeFormat("en", {
    weekday: "long",
    month: "short",
    day: "numeric",
    year: "numeric"
  }).format(new Date(`${value}T12:00:00`));
}

function addDays(date, days) {
  const next = new Date(date);
  next.setDate(next.getDate() + days);
  return next;
}

function toDateInputValue(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function normalizePhone(value) {
  return value.replace(/[^\d+]/g, "");
}

function formatPhone(countryCode, localNumber) {
  const digits = normalizePhone(localNumber).replace(/^\+/, "");
  return `${countryCode} ${digits}`.trim();
}

function isApprovedEmail(value) {
  return /^[A-Za-z0-9._%+-]+@(gmail|yahoo)\.com$/.test(value.trim());
}

function getAvailableTimeSlots(date, appointments) {
  const bookedTimes = appointments
    .filter((appointment) => appointment.date === date)
    .map((appointment) => appointment.time);

  return timeSlots.filter((slot) => !bookedTimes.includes(slot));
}

function getBookingError(form, appointments) {
  if (!form.patient.trim() || !form.countryCode || !form.phoneNumber.trim() || !form.email.trim()) {
    return "Please complete the patient name, phone country code, phone number, and email.";
  }

  if (form.date < earliestBookingDate) {
    return `Bookings can only be created from ${formatDate(earliestBookingDate)} onward.`;
  }

  // basic phone number validation: digits only and reasonable length
  const digits = normalizePhone(form.phoneNumber);
  if (digits.length < 6 || digits.length > 14) {
    return "Phone number must contain between 6 and 14 digits (local part).";
  }

  if (!isApprovedEmail(form.email)) {
    return "Email must use an approved domain like xyz@gmail.com or xyz@yahoo.com.";
  }

  if (!form.time) {
    return "There are no available appointment times for the selected date.";
  }

  const hasTimeConflict = appointments.some(
    (appointment) => appointment.date === form.date && appointment.time === form.time
  );

  if (hasTimeConflict) {
    return "This appointment time is already booked for the selected date.";
  }

  const cleanPhone = normalizePhone(formatPhone(form.countryCode, form.phoneNumber));
  const hasPhoneConflict = appointments.some(
    (appointment) =>
      normalizePhone(appointment.phone) === cleanPhone &&
      appointment.date === form.date &&
      appointment.time === form.time
  );

  if (hasPhoneConflict) {
    return "This phone number already has an appointment at the selected date and time.";
  }

  return "";
}

function mapServerToClient(row) {
  if (!row) return null;
  let dateStr = '';
  if (typeof row.appointment_date === 'string') {
    // Handle 'YYYY-MM-DD' or ISO strings like '2026-06-29T22:00:00.000Z'
    const isoMatch = row.appointment_date.match(/^(\d{4}-\d{2}-\d{2})/);
    dateStr = isoMatch ? isoMatch[1] : row.appointment_date.slice(0, 10);
  } else if (row.appointment_date?.toISOString) {
    dateStr = row.appointment_date.toISOString().slice(0, 10);
  }
  const timeStr = (row.appointment_time || '').toString().slice(0, 5);
  return {
    id: row.id,
    patientId: row.patient_id,
    patient: row.patient_name,
    phone: row.phone,
    email: row.email,
    serviceId: row.service_id,
    doctorId: row.doctor_id,
    date: dateStr || '',
    time: timeStr,
    status: row.status || 'Pending',
    notes: row.notes || ''
  };
}

createRoot(document.getElementById("root")).render(<App />);
