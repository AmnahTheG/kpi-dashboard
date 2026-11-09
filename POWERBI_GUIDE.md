# Power BI Connection Guide
## Connecting Power BI to your MySQL KPI Database

This guide walks you through connecting Power BI Desktop to the MySQL database
and building the dashboard visuals.

---

## Step 1 — Install the MySQL connector for Power BI

Power BI does not connect to MySQL natively without a driver.

1. Download **MySQL Connector/NET** from:
   https://dev.mysql.com/downloads/connector/net/
2. Install it on your Windows machine.
3. Restart Power BI Desktop.

---

## Step 2 — Connect Power BI to MySQL

1. Open **Power BI Desktop**
2. Click **Home → Get Data → More…**
3. Search for **MySQL database** and click **Connect**
4. Enter:
   - Server:   `localhost`
   - Database: `kpi_dashboard`
5. Click **OK**, enter your MySQL username and password
6. In the Navigator window, select the **`kpi_performance`** view
7. Click **Load**

> 💡 The `kpi_performance` view already joins users, departments, KPIs,
>    and entries into one clean flat table — you don't need to manage
>    relationships in Power BI yourself.

---

## Step 3 — Fields in the `kpi_performance` view

| Column           | What it contains                        |
|------------------|-----------------------------------------|
| `period`         | Time period (e.g. "2024-11")            |
| `actual_value`   | The recorded value for that period      |
| `target`         | The numeric goal                        |
| `achievement_pct`| actual / target × 100 (%)              |
| `status`         | "On Track", "Near Target", "Below Target"|
| `kpi_name`       | Name of the KPI                         |
| `unit`           | Unit of measurement ($, %, tickets…)    |
| `frequency`      | daily / weekly / monthly                |
| `department`     | Department that owns the KPI            |
| `owner`          | Name of the user who created the KPI    |
| `note`           | Any comment logged with the entry       |

---

## Step 4 — Recommended Visuals to Build

### Visual 1 — KPI Status Card (Card Visual)
- Field: `achievement_pct` (Average)
- Add a filter for a specific `kpi_name`
- Add conditional formatting: green ≥ 100, yellow ≥ 80, red < 80

### Visual 2 — Actual vs Target Over Time (Line Chart)
- X-axis: `period`
- Y-axis: `actual_value` and `target` as two separate lines
- Legend: auto

### Visual 3 — Department Performance (Bar Chart)
- X-axis: `department`
- Y-axis: Average of `achievement_pct`
- Color: conditional on status

### Visual 4 — KPI Status Overview (Donut Chart)
- Legend: `status`
- Values: Count of `entry_id`
- Shows how many entries are On Track vs Below Target

### Visual 5 — Slicer (for filtering)
- Field: `department`
- Type: Dropdown
- Connects to all visuals on the page automatically

---

## Step 5 — Auto-refresh (optional)

If you publish to Power BI Service (cloud), you can set a scheduled refresh
so the dashboard updates automatically when new data is logged through the
Flask web app.

1. Publish report: **Home → Publish → My Workspace**
2. In Power BI Service → Dataset → Scheduled Refresh
3. Set frequency (e.g. daily at 8:00 AM)

---

## Tips

- Use **Ctrl+D** to duplicate a visual and change the KPI filter — fast way
  to build a multi-KPI dashboard
- Use a **Text Box** on the canvas to add your name and a short description —
  looks professional in a portfolio
- Export as PDF: **File → Export → PDF** — share with recruiters directly
