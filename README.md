# 📊 Business KPI Dashboard

A full-stack web application that lets teams **define KPIs, log actual performance data, and visualize results in Power BI** — built using Python, MySQL, and Flask.

> Portfolio project by **Amnah Alshwail** — MIS Graduate | Power BI | MySQL | Python

---

## 🖼️ Screenshots

> *(Add your Power BI dashboard screenshot here after connecting)*

---

## 🎯 What This Project Does

| Feature | Description |
|---|---|
| **User Authentication** | Register and login with hashed passwords. Roles: Admin and Viewer. |
| **KPI Management** | Create, track, and delete KPIs with targets, units, departments, and frequency. |
| **Data Entry** | Log actual values per time period (monthly, weekly, daily). |
| **Live Dashboard** | Cards showing latest value, target, achievement %, and color-coded status. |
| **Power BI Integration** | A pre-built SQL View (`kpi_performance`) connects directly to Power BI for rich charts. |

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **Backend** | Python + Flask | Lightweight web framework, Python is readable and industry standard |
| **Database** | MySQL | Relational database, matches MIS curriculum and real enterprise use |
| **Frontend** | HTML + CSS + JavaScript | No framework needed — keeps the project simple and accessible |
| **BI Layer** | Power BI Desktop | Professional data visualization, connects natively to MySQL |

---

## 📁 Project Structure

```
kpi-dashboard-v2/
├── app.py                  ← Flask web server (routes, auth, API)
├── requirements.txt        ← Python dependencies
├── .env.example            ← Template for environment variables
├── .gitignore
│
├── database/
│   ├── schema.sql          ← MySQL table definitions + kpi_performance view
│   └── seed_data.py        ← Inserts realistic sample data for demo/testing
│
├── templates/
│   ├── login.html          ← Login + Register page
│   └── dashboard.html      ← Main KPI dashboard page
│
└── POWERBI_GUIDE.md        ← Step-by-step guide to connect Power BI to MySQL
```

---

## 🚀 How to Run This Project

### Prerequisites
- Python 3.10+
- MySQL Server (MySQL Community Edition — free)
- MySQL Workbench (optional but helpful)
- Power BI Desktop (free from Microsoft)

---

### Step 1 — Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/kpi-dashboard.git
cd kpi-dashboard
```

### Step 2 — Create the MySQL database
Open **MySQL Workbench** and run:
```sql
SOURCE database/schema.sql;
```
Or from terminal:
```bash
mysql -u root -p < database/schema.sql
```

### Step 3 — Set up environment variables
```bash
cp .env.example .env
```
Then open `.env` and fill in your MySQL password.

### Step 4 — Install Python packages
```bash
pip install -r requirements.txt
```

### Step 5 — Seed sample data (optional but recommended)
Edit `database/seed_data.py` — change the MySQL password on line 17 — then run:
```bash
python database/seed_data.py
```
This inserts 8 KPIs with 12 months of realistic data so Power BI has something to visualize immediately.

### Step 6 — Start the web app
```bash
python app.py
```
Open: **http://localhost:5000**

Register an account, then start creating and tracking KPIs.

### Step 7 — Connect Power BI
Follow the full guide in [POWERBI_GUIDE.md](POWERBI_GUIDE.md) to connect Power BI Desktop to MySQL and build the visuals.

---

## 🗄️ Database Design

```
users        → stores login credentials and roles
departments  → lookup table for department names
kpis         → each KPI: name, unit, target, frequency, owner, department
entries      → actual recorded values per period
kpi_performance (VIEW) → flat join of all tables, used by Power BI
```

**Key design decisions:**
- `entries.period` is stored as text (`"2024-11"`, `"2024-W45"`) — handles monthly, weekly, and daily flexibly
- Passwords are hashed with **bcrypt** — never stored as plain text
- The `kpi_performance` **VIEW** pre-joins all tables so Power BI connects to one clean, flat table instead of navigating foreign keys

---

## 🔐 API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/register` | No | Create a new user account |
| POST | `/api/login` | No | Login and start a session |
| POST | `/api/logout` | No | End the session |
| GET | `/api/kpis` | ✅ | List KPIs |
| POST | `/api/kpis` | ✅ | Create a KPI |
| DELETE | `/api/kpis/<id>` | ✅ | Delete a KPI |
| GET | `/api/entries?kpi_id=X` | ✅ | Get all entries for a KPI |
| POST | `/api/entries` | ✅ | Log a new data entry |
| DELETE | `/api/entries/<id>` | ✅ | Delete an entry |

---

## 💡 Business Context (MIS Perspective)

This project simulates a real business need:
- **Managers** want visibility into KPIs without manually checking spreadsheets
- **Departments** (Sales, Marketing, IT, HR, Operations) each own their metrics
- **Power BI** is the industry-standard tool for turning database data into executive-level visuals
- The **alert system** (color-coded status) mimics what enterprise BI tools like SAP and Oracle Analytics do

---

## 🗺️ Roadmap

- [ ] CSV import — bulk-upload historical data from Excel
- [ ] Email alert when a KPI falls below 80% of target
- [ ] Forecasting tab using Python's `statsmodels` library
- [ ] Deploy to a cloud server (AWS EC2 or Heroku)

---

## 👤 Author

**Amnah Alshwail**  
MIS Graduate, Imam Abdulrahman bin Faisal University  
[LinkedIn](https://www.linkedin.com/in/amnah-alshwail) | [GitHub](https://github.com/YOUR_USERNAME)
