require('dotenv').config();

(async () => {
  try {
    const payload = {
      patient_name: "Test New",
      phone: "+49 17000000000",
      email: "newtest@example.com",
      service_id: "general",
      doctor_id: "amara",
      appointment_date: "2026-06-26",
      appointment_time: "13:00",
      notes: "test create"
    };

    const res = await fetch('http://localhost:5000/api/appointments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    console.log('status', res.status);
    console.log('body', data);
  } catch (err) {
    console.error('ERROR', err);
    process.exit(1);
  }
})();
