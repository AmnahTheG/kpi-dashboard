# seed_data.py
# ---------------------------------------------------------------
# Populates the database with realistic sample data so you can
# immediately connect Power BI and see charts working.
#
# Run once after creating the schema:
#   python seed_data.py
# ---------------------------------------------------------------

import mysql.connector
from datetime import datetime

# ── Database connection ────────────────────────────────────────
# Change these values to match your MySQL setup
conn = mysql.connector.connect(
    host     = "localhost",
    user     = "root",
    password = "your_mysql_password",   # ← change this
    database = "kpi_dashboard"
)
cursor = conn.cursor()

print("Connected to MySQL. Seeding data...")

# ── Departments ────────────────────────────────────────────────
departments = ["Sales", "Marketing", "Operations", "HR", "IT"]
for dept in departments:
    cursor.execute(
        "INSERT IGNORE INTO departments (name) VALUES (%s)",
        (dept,)
    )

conn.commit()
print(f"  ✓ Inserted {len(departments)} departments")

# ── Admin user ────────────────────────────────────────────────
# Password stored as plain text here for simplicity in seeding.
# The Flask app will use bcrypt when real users register.
cursor.execute("""
    INSERT IGNORE INTO users (name, email, password, role)
    VALUES (%s, %s, %s, %s)
""", ("Amnah Admin", "admin@demo.com", "hashed_password_here", "admin"))

conn.commit()

cursor.execute("SELECT id FROM users WHERE email = 'admin@demo.com'")
admin_id = cursor.fetchone()[0]
print(f"  ✓ Admin user created (id={admin_id})")

# ── KPIs ──────────────────────────────────────────────────────
# Each KPI: (user_id, dept_name, name, unit, target, frequency)
kpi_definitions = [
    ("Sales",      "Monthly Revenue",           "$",       50000, "monthly"),
    ("Sales",      "New Customers Acquired",     "clients",   20, "monthly"),
    ("Marketing",  "Website Traffic",            "visits",  5000, "monthly"),
    ("Marketing",  "Lead Conversion Rate",       "%",         15, "monthly"),
    ("Operations", "Support Tickets Resolved",   "tickets",  200, "monthly"),
    ("Operations", "Average Resolution Time",    "hours",      4, "monthly"),
    ("HR",         "Employee Satisfaction Score","score",     80, "monthly"),
    ("IT",         "System Uptime",              "%",       99.5, "monthly"),
]

kpi_ids = {}
for dept_name, kpi_name, unit, target, freq in kpi_definitions:
    cursor.execute("SELECT id FROM departments WHERE name = %s", (dept_name,))
    dept_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO kpis (user_id, department_id, name, unit, target, frequency)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (admin_id, dept_id, kpi_name, unit, target, freq))

    conn.commit()
    kpi_ids[kpi_name] = cursor.lastrowid

print(f"  ✓ Inserted {len(kpi_ids)} KPIs")

# ── Entries (12 months of data) ────────────────────────────────
# Realistic data with some months above target and some below
import random
random.seed(42)  # fixed seed so results are reproducible

monthly_data = {
    "Monthly Revenue": [
        42000, 47000, 53000, 49000, 55000, 61000,
        58000, 44000, 51000, 63000, 57000, 66000
    ],
    "New Customers Acquired": [
        15, 18, 22, 20, 25, 23, 17, 19, 26, 28, 21, 30
    ],
    "Website Traffic": [
        3900, 4200, 4800, 5100, 5500, 4900,
        4400, 5200, 5700, 6100, 5300, 5800
    ],
    "Lead Conversion Rate": [
        11, 13, 14, 16, 15, 17, 12, 14, 18, 16, 15, 19
    ],
    "Support Tickets Resolved": [
        180, 195, 210, 205, 215, 198, 170, 220, 230, 210, 225, 240
    ],
    "Average Resolution Time": [
        5.2, 4.8, 4.1, 3.9, 3.7, 4.2, 5.0, 3.8, 3.5, 3.6, 3.4, 3.2
    ],
    "Employee Satisfaction Score": [
        72, 74, 77, 76, 79, 81, 78, 80, 83, 82, 85, 87
    ],
    "System Uptime": [
        99.1, 99.5, 99.8, 98.9, 99.6, 99.9,
        99.3, 99.7, 99.9, 99.5, 99.8, 99.9
    ],
}

periods = [
    "2024-01","2024-02","2024-03","2024-04","2024-05","2024-06",
    "2024-07","2024-08","2024-09","2024-10","2024-11","2024-12"
]

entry_count = 0
for kpi_name, values in monthly_data.items():
    kpi_id = kpi_ids.get(kpi_name)
    if not kpi_id:
        continue
    for period, value in zip(periods, values):
        cursor.execute("""
            INSERT INTO entries (kpi_id, value, period)
            VALUES (%s, %s, %s)
        """, (kpi_id, value, period))
        entry_count += 1

conn.commit()
print(f"  ✓ Inserted {entry_count} entries (12 months × 8 KPIs)")

cursor.close()
conn.close()

print("\n✅ Database seeded successfully!")
print("   You can now connect Power BI to MySQL and use the 'kpi_performance' view.")
