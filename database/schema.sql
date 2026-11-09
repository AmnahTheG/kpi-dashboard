-- ============================================================
-- KPI Dashboard - MySQL Schema
-- ============================================================
-- Run this file in MySQL Workbench or via the terminal:
--   mysql -u root -p kpi_dashboard < schema.sql
-- ============================================================

-- Create the database (skip if already created)
CREATE DATABASE IF NOT EXISTS kpi_dashboard;
USE kpi_dashboard;

-- ── users ─────────────────────────────────────────────────────
-- Stores login credentials for each user.
-- Passwords are stored as bcrypt hashes — never plain text.
-- role: 'admin' can see all KPIs; 'viewer' sees only their own.
CREATE TABLE IF NOT EXISTS users (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(100) NOT NULL,
  email      VARCHAR(150) NOT NULL UNIQUE,
  password   VARCHAR(255) NOT NULL,
  role       ENUM('admin', 'viewer') NOT NULL DEFAULT 'viewer',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ── departments ───────────────────────────────────────────────
-- Optional lookup table for department names.
-- Makes Power BI filtering/slicing by department much cleaner.
CREATE TABLE IF NOT EXISTS departments (
  id   INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE
);

-- ── kpis ──────────────────────────────────────────────────────
-- Each KPI belongs to a user and a department.
-- 'target' is the numeric goal (e.g. 50000 for $50,000 monthly sales).
-- 'unit' describes what the number means (e.g. '$', '%', 'tickets').
-- 'frequency' tells how often to expect a new entry.
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

-- ── entries ───────────────────────────────────────────────────
-- The actual recorded values for each KPI over time.
-- 'period' is a human-readable label: '2024-11', '2024-W45', '2024-10-01'
-- This table is what Power BI will query for charts and visuals.
CREATE TABLE IF NOT EXISTS entries (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  kpi_id     INT NOT NULL,
  value      DECIMAL(15,2) NOT NULL,
  period     VARCHAR(20)   NOT NULL,
  note       TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (kpi_id) REFERENCES kpis(id) ON DELETE CASCADE
);

-- ── Useful view for Power BI ───────────────────────────────────
-- This VIEW joins all 3 tables so Power BI connects to one clean table
-- instead of having to understand all the relationships itself.
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
JOIN kpis k        ON e.kpi_id     = k.id
LEFT JOIN departments d ON k.department_id = d.id
JOIN users u       ON k.user_id    = u.id;
