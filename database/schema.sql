-- KPI Dashboard — MySQL Schema
-- Run once to initialize the database:
--   mysql -u root -p kpi_dashboard < schema.sql

CREATE DATABASE IF NOT EXISTS kpi_dashboard;
USE kpi_dashboard;

CREATE TABLE IF NOT EXISTS users (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(100) NOT NULL,
  email      VARCHAR(150) NOT NULL UNIQUE,
  password   VARCHAR(255) NOT NULL,
  role       ENUM('admin', 'viewer') NOT NULL DEFAULT 'viewer',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS departments (
  id   INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS kpis (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  user_id       INT NOT NULL,
  department_id INT,
  name          VARCHAR(200) NOT NULL,
  unit          VARCHAR(20)  NOT NULL,
  target        DECIMAL(15,2) NOT NULL,
  frequency     ENUM('daily', 'weekly', 'monthly') NOT NULL DEFAULT 'monthly',
  created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id)       REFERENCES users(id)       ON DELETE CASCADE,
  FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS entries (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  kpi_id     INT NOT NULL,
  value      DECIMAL(15,2) NOT NULL,
  period     VARCHAR(20)   NOT NULL,
  note       TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (kpi_id) REFERENCES kpis(id) ON DELETE CASCADE
);

-- Flat view used by Power BI — joins all tables into one queryable surface
CREATE OR REPLACE VIEW kpi_performance AS
SELECT
  e.id          AS entry_id,
  e.period,
  e.value       AS actual_value,
  k.target,
  ROUND((e.value / k.target) * 100, 1)   AS achievement_pct,
  CASE
    WHEN (e.value / k.target) >= 1.0  THEN 'On Track'
    WHEN (e.value / k.target) >= 0.8  THEN 'Near Target'
    ELSE                                    'Below Target'
  END           AS status,
  k.name        AS kpi_name,
  k.unit,
  k.frequency,
  d.name        AS department,
  u.name        AS owner,
  e.note,
  e.created_at
FROM entries e
JOIN kpis k             ON e.kpi_id        = k.id
LEFT JOIN departments d ON k.department_id = d.id
JOIN users u            ON k.user_id       = u.id;
