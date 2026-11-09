# app.py
# ---------------------------------------------------------------
# KPI Dashboard - Python Flask Backend
#
# This is the web server. It handles:
#   - Showing the dashboard HTML page
#   - API endpoints to Create/Read/Update/Delete KPIs and entries
#   - Simple session-based login (no JWT needed for this scale)
#
# Run it:
#   python app.py
# Then open: http://localhost:5000
# ---------------------------------------------------------------

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import mysql.connector
import bcrypt
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change_this_before_deploying")

# ── Database connection helper ─────────────────────────────────
# Called at the start of every request that needs the database.
def get_db():
    return mysql.connector.connect(
        host     = os.environ.get("DB_HOST",     "localhost"),
        user     = os.environ.get("DB_USER",     "root"),
        password = os.environ.get("DB_PASSWORD", "your_mysql_password"),
        database = os.environ.get("DB_NAME",     "kpi_dashboard")
    )

# ── Auth helper ────────────────────────────────────────────────
def current_user():
    """Returns the logged-in user dict from the session, or None."""
    return session.get("user")

def login_required(fn):
    """Decorator: redirects to /login if user is not logged in."""
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user():
            return redirect(url_for("login_page"))
        return fn(*args, **kwargs)
    return wrapper

# ════════════════════════════════════════════════════════════════
#  AUTH ROUTES
# ════════════════════════════════════════════════════════════════

@app.route("/")
@login_required
def index():
    return render_template("dashboard.html", user=current_user())

@app.route("/login", methods=["GET"])
def login_page():
    if current_user():
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/api/login", methods=["POST"])
def api_login():
    data     = request.get_json()
    email    = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    db     = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    # bcrypt.checkpw compares plain password against the stored hash
    if not user or not bcrypt.checkpw(password.encode(), user["password"].encode()):
        return jsonify({"error": "Invalid credentials"}), 401

    # Store safe user info in the server session (no password!)
    session["user"] = {"id": user["id"], "name": user["name"], "email": user["email"], "role": user["role"]}
    return jsonify({"message": "Logged in", "user": session["user"]})

@app.route("/api/register", methods=["POST"])
def api_register():
    data     = request.get_json()
    name     = data.get("name", "").strip()
    email    = data.get("email", "").strip()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"error": "name, email, and password are required"}), 400

    # Hash the password — bcrypt automatically handles the salt
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        db     = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, hashed)
        )
        db.commit()
        cursor.close()
        db.close()
        return jsonify({"message": "Account created"}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Email already registered"}), 409

@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"message": "Logged out"})

# ════════════════════════════════════════════════════════════════
#  KPI ROUTES
# ════════════════════════════════════════════════════════════════

@app.route("/api/kpis", methods=["GET"])
@login_required
def get_kpis():
    db     = get_db()
    cursor = db.cursor(dictionary=True)
    user   = current_user()

    if user["role"] == "admin":
        cursor.execute("""
            SELECT k.*, d.name AS department, u.name AS owner
            FROM kpis k
            LEFT JOIN departments d ON k.department_id = d.id
            JOIN users u ON k.user_id = u.id
            ORDER BY k.created_at DESC
        """)
    else:
        cursor.execute("""
            SELECT k.*, d.name AS department, u.name AS owner
            FROM kpis k
            LEFT JOIN departments d ON k.department_id = d.id
            JOIN users u ON k.user_id = u.id
            WHERE k.user_id = %s
            ORDER BY k.created_at DESC
        """, (user["id"],))

    kpis = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(kpis)

@app.route("/api/kpis", methods=["POST"])
@login_required
def create_kpi():
    data        = request.get_json()
    name        = data.get("name")
    unit        = data.get("unit")
    target      = data.get("target")
    frequency   = data.get("frequency", "monthly")
    dept_name   = data.get("department", "General")

    if not name or not unit or target is None:
        return jsonify({"error": "name, unit, and target are required"}), 400

    db     = get_db()
    cursor = db.cursor()

    # Get or create the department
    cursor.execute("SELECT id FROM departments WHERE name = %s", (dept_name,))
    row = cursor.fetchone()
    if row:
        dept_id = row[0]
    else:
        cursor.execute("INSERT INTO departments (name) VALUES (%s)", (dept_name,))
        db.commit()
        dept_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO kpis (user_id, department_id, name, unit, target, frequency)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (current_user()["id"], dept_id, name, unit, float(target), frequency))
    db.commit()
    new_id = cursor.lastrowid

    cursor.close()
    db.close()
    return jsonify({"message": "KPI created", "id": new_id}), 201

@app.route("/api/kpis/<int:kpi_id>", methods=["DELETE"])
@login_required
def delete_kpi(kpi_id):
    db     = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM kpis WHERE id = %s", (kpi_id,))
    kpi = cursor.fetchone()
    if not kpi:
        return jsonify({"error": "KPI not found"}), 404

    user = current_user()
    if kpi["user_id"] != user["id"] and user["role"] != "admin":
        return jsonify({"error": "Forbidden"}), 403

    cursor.execute("DELETE FROM kpis WHERE id = %s", (kpi_id,))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({"message": "KPI deleted"})

# ════════════════════════════════════════════════════════════════
#  ENTRY ROUTES
# ════════════════════════════════════════════════════════════════

@app.route("/api/entries", methods=["GET"])
@login_required
def get_entries():
    kpi_id = request.args.get("kpi_id")
    if not kpi_id:
        return jsonify({"error": "kpi_id is required"}), 400

    db     = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM entries WHERE kpi_id = %s ORDER BY period ASC",
        (kpi_id,)
    )
    entries = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(entries)

@app.route("/api/entries", methods=["POST"])
@login_required
def create_entry():
    data   = request.get_json()
    kpi_id = data.get("kpi_id")
    value  = data.get("value")
    period = data.get("period")
    note   = data.get("note", "")

    if not kpi_id or value is None or not period:
        return jsonify({"error": "kpi_id, value, and period are required"}), 400

    db     = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO entries (kpi_id, value, period, note) VALUES (%s, %s, %s, %s)",
        (kpi_id, float(value), period, note)
    )
    db.commit()
    new_id = cursor.lastrowid
    cursor.close()
    db.close()
    return jsonify({"message": "Entry logged", "id": new_id}), 201

@app.route("/api/entries/<int:entry_id>", methods=["DELETE"])
@login_required
def delete_entry(entry_id):
    db     = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM entries WHERE id = %s", (entry_id,))
    entry = cursor.fetchone()
    if not entry:
        return jsonify({"error": "Entry not found"}), 404

    cursor.execute("DELETE FROM entries WHERE id = %s", (entry_id,))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({"message": "Entry deleted"})

# ════════════════════════════════════════════════════════════════
#  DEPARTMENTS LIST (for dropdowns)
# ════════════════════════════════════════════════════════════════

@app.route("/api/departments", methods=["GET"])
@login_required
def get_departments():
    db     = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM departments ORDER BY name")
    depts = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(depts)

# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app.run(debug=True, port=5000)
