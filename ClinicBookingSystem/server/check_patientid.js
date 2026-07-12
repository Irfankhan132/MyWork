require('dotenv').config();
const pool = require('./db');

(async () => {
  try {
    const columns = await pool.query("SELECT column_name FROM information_schema.columns WHERE table_name='appointments' ORDER BY ordinal_position");
    console.log('columns:', columns.rows.map(r => r.column_name).join(','));
    const row = await pool.query("SELECT id, patient_id, patient_name, email, phone FROM appointments ORDER BY id DESC LIMIT 5");
    console.log('rows:', row.rows);
  } catch (err) {
    console.error('error', err);
  } finally {
    await pool.end();
  }
})();
