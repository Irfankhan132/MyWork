require('dotenv').config();
const { Pool } = require('pg');

const pool = new Pool({
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  database: process.env.DB_NAME,
  connectionTimeoutMillis: 5000
});

(async () => {
  try {
    const res = await pool.query('SELECT NOW() as now');
    console.log('OK: connected to database. Server time:', res.rows[0].now);
  } catch (err) {
    console.error('ERROR: failed to connect to database:');
    console.error(err.message || err);
    process.exitCode = 1;
  } finally {
    await pool.end();
  }
})();
