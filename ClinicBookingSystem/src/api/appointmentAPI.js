import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// Appointments API
export const appointmentAPI = {
  // Admin login
  login: async ({ username, password }) => {
    try {
      const response = await api.post('/admin/login', { username, password });
      return response.data;
    } catch (error) {
      if (error.response?.status === 401) {
        throw new Error(error.response.data.error || 'Invalid credentials');
      }
      console.error('Error logging in:', error);
      throw error;
    }
  },

  // Get all appointments
  getAll: async (token) => {
    try {
      const response = await api.get('/appointments', { headers: authHeaders(token) });
      return response.data;
    } catch (error) {
      console.error('Error fetching appointments:', error);
      throw error;
    }
  },

  // Get appointments by date
  getByDate: async (date) => {
    try {
      const response = await api.get(`/appointments/date/${date}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching appointments by date:', error);
      throw error;
    }
  },

  // Get booked time slots for a doctor on a specific date
  getBookedSlots: async (doctorId, date) => {
    try {
      const response = await api.get(`/appointments/booked-slots/${doctorId}/${date}`);
      return response.data.bookedSlots;
    } catch (error) {
      console.error('Error fetching booked slots:', error);
      throw error;
    }
  },

  // Create new appointment
  create: async (appointmentData) => {
    try {
      const payload = {
        patient_name: appointmentData.patient_name ?? appointmentData.patient,
        phone: appointmentData.phone,
        email: appointmentData.email,
        service_id: appointmentData.service_id ?? appointmentData.serviceId,
        doctor_id: appointmentData.doctor_id ?? appointmentData.doctorId,
        appointment_date: appointmentData.appointment_date ?? appointmentData.date,
        appointment_time: appointmentData.appointment_time ?? appointmentData.time,
        notes: appointmentData.notes,
      };
      const response = await api.post('/appointments', payload);
      return response.data;
    } catch (error) {
      if (error.response?.status === 400) {
        throw new Error(error.response.data.error || 'Failed to create appointment');
      }
      console.error('Error creating appointment:', error);
      throw error;
    }
  },

  // Update appointment
  update: async (id, updates, token) => {
    try {
      const payload = {};
      if (typeof updates.status !== 'undefined') payload.status = updates.status;
      if (typeof updates.notes !== 'undefined') payload.notes = updates.notes;
      if (typeof updates.date !== 'undefined') payload.appointment_date = updates.date;
      if (typeof updates.time !== 'undefined') payload.appointment_time = updates.time;

      const response = await api.put(
        `/appointments/${id}`,
        payload,
        { headers: authHeaders(token) }
      );
      return response.data;
    } catch (error) {
      console.error('Error updating appointment:', error);
      throw error;
    }
  },

  // Delete appointment
  delete: async (id, token) => {
    try {
      const response = await api.delete(`/appointments/${id}`, { headers: authHeaders(token) });
      return response.data;
    } catch (error) {
      console.error('Error deleting appointment:', error);
      throw error;
    }
  },

  // Search appointments
  search: async (query) => {
    try {
      const response = await api.get(`/appointments/search/${query}`);
      return response.data;
    } catch (error) {
      console.error('Error searching appointments:', error);
      throw error;
    }
  },
};

export default api;
