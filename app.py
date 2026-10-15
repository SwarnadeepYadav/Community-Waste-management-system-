"""Main Flask application: every web page (route) of the project lives here."""
import os, sqlite3, uuid
from datetime import date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from init_db import init_db, DB_PATH

BASE = os.path.dirname(os.path.abspath(__file__))
UPLOADS = os.path.join(BASE, "static", "uploads")
ALLOWED = {"png", "jpg", "jpeg", "gif", "webp"}
STATUSES = ["Pending", "Assigned", "In Progress", "Resolved"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

CATEGORIES = [
    {"name": "Wet Waste", "icon": "🍌", "examples": "Food leftovers, vegetable peels, fruit waste, flowers",
     "disposal": "Keep in a green bin. Convert into compost at home or give to the municipal wet-waste vehicle. Never mix with plastic."},
    {"name": "Dry Waste", "icon": "📦", "examples": "Paper, cardboard, glass, metal, cloth, wood",
     "disposal": "Keep clean and dry in a blue bin. Hand over to the collector or a scrap dealer so it can be recycled."},
    {"name": "Plastic Waste", "icon": "🧴", "examples": "Bottles, carry bags, wrappers, containers",
     "disposal": "Rinse and dry, then store separately. Give to plastic recycling centres. Avoid burning plastic."},
    {"name": "E-Waste", "icon": "🔌", "examples": "Old phones, chargers, batteries, monitors, cables",
     "disposal": "Never throw in normal bins. Give to authorised e-waste collection centres or company take-back programmes."},
    {"name": "Hazardous Waste", "icon": "☣️", "examples": "Paint, chemicals, tube lights, sanitary and medical waste, pesticides",
     "disposal": "Keep in a sealed, labelled container in a red bin. Hand over only on hazardous-waste collection day."},
    {"name": "Other Waste", "icon": "🗑️", "examples": "Construction debris, garden trimmings, bulky items",
     "disposal": "Do not leave on roads. Report it here or contact the municipal office for special pick-up."}]
CATEGORY_NAMES = [c["name"] for c in CATEGORIES]

app = Flask(__name__)
app.secret_key = "change-this-secret-key-before-real-use"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024   # 5 MB upload limit
os.makedirs(UPLOADS, exist_ok=True)
if not os.path.exists(DB_PATH):
    init_db()

# ---------- database helpers ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db: db.close()

@app.template_filter("cid")
def complaint_id(n):
    return f"WC-{n:04d}"

def login_required(role=None):
    def deco(f):
        @wraps(f)
        def wrapper(*a, **k):
            if "role" not in session:
                flash("Please log in first.", "error"); return redirect(url_for("login"))
            if role and session["role"] != role:
                flash("You do not have access to that page.", "error"); return redirect(url_for("home"))
            return f(*a, **k)
        return wrapper
    return deco

def complaint_query(extra_where="", extra_params=()):
    """Builds the complaint list query with search/filter from the URL (?location=&waste_type=&status=&date=)."""
    sql = ("SELECT c.*, u.name AS user_name, col.name AS collector_name FROM complaints c "
           "JOIN users u ON u.id=c.user_id LEFT JOIN collectors col ON col.id=c.collector_id WHERE 1=1 " + extra_where)
    params = list(extra_params)
    if request.args.get("location"):
        sql += " AND c.location LIKE ?"; params.append("%" + request.args["location"] + "%")
    if request.args.get("waste_type"):
        sql += " AND c.waste_type=?"; params.append(request.args["waste_type"])
    if request.args.get("status"):
        sql += " AND c.status=?"; params.append(request.args["status"])
    if request.args.get("date"):
        sql += " AND c.report_date=?"; params.append(request.args["date"])
    return get_db().execute(sql + " ORDER BY c.id DESC", params).fetchall()

# ---------- public pages ----------
@app.route("/")
def home():
    db = get_db()
    total = db.execute("SELECT COALESCE(SUM(quantity_kg),0) FROM waste_reports").fetchone()[0]
    pending = db.execute("SELECT COUNT(*) FROM complaints WHERE status!='Resolved'").fetchone()[0]  # pending = not yet resolved
    resolved = db.execute("SELECT COUNT(*) FROM complaints WHERE status='Resolved'").fetchone()[0]
    today = date.today().weekday()
    rows = [dict(r, ahead=(DAYS.index(r["day"]) - today) % 7) for r in db.execute("SELECT * FROM schedules")]
    upcoming = sorted(rows, key=lambda r: r["ahead"])[:3]
    return render_template("index.html", total=round(total), pending=pending, resolved=resolved, upcoming=upcoming)

@app.route("/categories")
def categories():
    return render_template("categories.html", categories=CATEGORIES)

@app.route("/schedule")
def schedule():
    rows = get_db().execute("SELECT * FROM schedules").fetchall()
    rows = sorted(rows, key=lambda r: (DAYS.index(r["day"]), r["time"]))
    return render_template("schedule.html", schedules=rows)

@app.route("/awareness")
def awareness():
    return render_template("awareness.html")

@app.route("/statistics")
def statistics():
    return render_template("statistics.html")

@app.route("/api/stats")
def api_stats():
    db = get_db()
    def pairs(sql):
        rows = db.execute(sql).fetchall(); return {"labels": [r[0] for r in rows], "values": [round(r[1], 1) for r in rows]}
    return jsonify(
        by_category=pairs("SELECT category, SUM(quantity_kg) FROM waste_reports GROUP BY category"),
        complaints_by_type=pairs("SELECT waste_type, COUNT(*) FROM complaints GROUP BY waste_type"),
        by_status=pairs("SELECT status, COUNT(*) FROM complaints GROUP BY status"),
        monthly=pairs("SELECT strftime('%Y-%m', collected_on) m, SUM(quantity_kg) FROM waste_reports GROUP BY m ORDER BY m"))

# ---------- register / login ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        f = {k: request.form.get(k, "").strip() for k in ("name", "email", "mobile", "password", "address")}
        if not all(f.values()): flash("All fields are required.", "error")
        elif not (f["mobile"].isdigit() and len(f["mobile"]) == 10): flash("Mobile number must be 10 digits.", "error")
        elif len(f["password"]) < 6: flash("Password must be at least 6 characters.", "error")
        else:
            db = get_db()
            if db.execute("SELECT 1 FROM users WHERE email=?", (f["email"].lower(),)).fetchone():
                flash("This email is already registered.", "error")
            else:
                db.execute("INSERT INTO users (name,email,mobile,password,address) VALUES (?,?,?,?,?)",
                           (f["name"], f["email"].lower(), f["mobile"], generate_password_hash(f["password"]), f["address"]))
                db.commit(); flash("Registration successful! Please log in.", "success")
                return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role", "user")
        table = {"user": "users", "admin": "admins", "collector": "collectors"}.get(role, "users")
        row = get_db().execute(f"SELECT * FROM {table} WHERE email=?", (request.form.get("email", "").strip().lower(),)).fetchone()
        if row and check_password_hash(row["password"], request.form.get("password", "")):
            session.clear(); session.update(role=role, uid=row["id"], name=row["name"])
            flash(f"Welcome, {row['name']}!", "success")
            return redirect(url_for({"user": "home", "admin": "admin_dashboard", "collector": "collector_dashboard"}[role]))
        flash("Invalid email or password.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear(); flash("You have been logged out.", "success")
    return redirect(url_for("home"))

# ---------- user pages ----------
@app.route("/report", methods=["GET", "POST"])
@login_required("user")
def report():
    if request.method == "POST":
        wtype, loc = request.form.get("waste_type", ""), request.form.get("location", "").strip()
        desc, when = request.form.get("description", "").strip(), request.form.get("date", "")
        if wtype not in CATEGORY_NAMES or not (loc and desc and when):
            flash("Please fill in all the fields.", "error"); return redirect(url_for("report"))
        filename, file = None, request.files.get("image")
        if file and file.filename:
            ext = file.filename.rsplit(".", 1)[-1].lower()
            if ext not in ALLOWED:
                flash("Only image files (png, jpg, jpeg, gif, webp) are allowed.", "error"); return redirect(url_for("report"))
            filename = uuid.uuid4().hex + "." + ext
            file.save(os.path.join(UPLOADS, filename))
        db = get_db()
        cur = db.execute("INSERT INTO complaints (user_id,waste_type,location,description,report_date,image) VALUES (?,?,?,?,?,?)",
                         (session["uid"], wtype, loc, desc, when, filename))
        db.commit(); flash(f"Complaint {complaint_id(cur.lastrowid)} submitted successfully.", "success")
        return redirect(url_for("my_complaints"))
    return render_template("report.html", categories=CATEGORY_NAMES, today=date.today().isoformat())

@app.route("/my-complaints")
@login_required("user")
def my_complaints():
    rows = complaint_query("AND c.user_id=?", (session["uid"],))
    return render_template("my_complaints.html", complaints=rows, categories=CATEGORY_NAMES, statuses=STATUSES)

# ---------- admin pages ----------
@app.route("/admin")
@login_required("admin")
def admin_dashboard():
    db = get_db()
    counts = {"users": db.execute("SELECT COUNT(*) FROM users").fetchone()[0],
              "collectors": db.execute("SELECT COUNT(*) FROM collectors").fetchone()[0],
              "complaints": db.execute("SELECT COUNT(*) FROM complaints").fetchone()[0],
              "pending": db.execute("SELECT COUNT(*) FROM complaints WHERE status!='Resolved'").fetchone()[0],
              "kg": round(db.execute("SELECT COALESCE(SUM(quantity_kg),0) FROM waste_reports").fetchone()[0])}
    return render_template("admin.html", complaints=complaint_query(), collectors=db.execute("SELECT * FROM collectors").fetchall(),
                           counts=counts, categories=CATEGORY_NAMES, statuses=STATUSES)

@app.route("/admin/complaint/<int:cid>", methods=["POST"])
@login_required("admin")
def admin_update_complaint(cid):
    status, collector = request.form.get("status"), request.form.get("collector_id") or None
    if status not in STATUSES: flash("Invalid status.", "error"); return redirect(url_for("admin_dashboard"))
    if collector and status == "Pending": status = "Assigned"   # assigning a collector moves it out of Pending
    db = get_db()
    db.execute("UPDATE complaints SET status=?, collector_id=? WHERE id=?", (status, collector, cid)); db.commit()
    flash(f"Complaint {complaint_id(cid)} updated.", "success")
    return redirect(request.referrer or url_for("admin_dashboard"))

@app.route("/admin/schedules", methods=["GET", "POST"])
@login_required("admin")
def admin_schedules():
    db = get_db()
    if request.method == "POST":
        db.execute("INSERT INTO schedules (area,waste_type,day,time,vehicle_no) VALUES (?,?,?,?,?)",
                   tuple(request.form[k] for k in ("area", "waste_type", "day", "time", "vehicle_no")))
        db.commit(); flash("Schedule added.", "success"); return redirect(url_for("admin_schedules"))
    return render_template("admin_schedules.html", schedules=db.execute("SELECT * FROM schedules ORDER BY area").fetchall(),
                           categories=CATEGORY_NAMES, days=DAYS)

@app.route("/admin/schedules/<int:sid>/update", methods=["POST"])
@login_required("admin")
def update_schedule(sid):
    db = get_db()
    db.execute("UPDATE schedules SET area=?,waste_type=?,day=?,time=?,vehicle_no=? WHERE id=?",
               tuple(request.form[k] for k in ("area", "waste_type", "day", "time", "vehicle_no")) + (sid,))
    db.commit(); flash("Schedule updated.", "success"); return redirect(url_for("admin_schedules"))

@app.route("/admin/schedules/<int:sid>/delete", methods=["POST"])
@login_required("admin")
def delete_schedule(sid):
    db = get_db(); db.execute("DELETE FROM schedules WHERE id=?", (sid,)); db.commit()
    flash("Schedule deleted.", "success"); return redirect(url_for("admin_schedules"))

@app.route("/admin/users", methods=["GET", "POST"])
@login_required("admin")
def admin_users():
    db = get_db()
    if request.method == "POST":   # add a new waste collector
        f = {k: request.form.get(k, "").strip() for k in ("name", "email", "mobile", "password", "vehicle_no", "area")}
        if not all(f.values()): flash("All collector fields are required.", "error")
        elif db.execute("SELECT 1 FROM collectors WHERE email=?", (f["email"].lower(),)).fetchone(): flash("Email already exists.", "error")
        else:
            db.execute("INSERT INTO collectors (name,email,mobile,password,vehicle_no,area) VALUES (?,?,?,?,?,?)",
                       (f["name"], f["email"].lower(), f["mobile"], generate_password_hash(f["password"]), f["vehicle_no"], f["area"]))
            db.commit(); flash("Collector added.", "success")
        return redirect(url_for("admin_users"))
    return render_template("admin_users.html", users=db.execute("SELECT * FROM users").fetchall(),
                           collectors=db.execute("SELECT * FROM collectors").fetchall())

@app.route("/admin/waste-reports")
@login_required("admin")
def admin_waste_reports():
    rows = get_db().execute("SELECT w.*, c.name AS collector_name FROM waste_reports w LEFT JOIN collectors c ON c.id=w.collector_id "
                            "ORDER BY w.collected_on DESC LIMIT 100").fetchall()
    return render_template("admin_waste.html", reports=rows)

# ---------- collector pages ----------
@app.route("/collector")
@login_required("collector")
def collector_dashboard():
    rows = complaint_query("AND c.collector_id=?", (session["uid"],))
    return render_template("collector.html", complaints=rows, statuses=STATUSES, categories=CATEGORY_NAMES)

@app.route("/collector/update/<int:cid>", methods=["POST"])
@login_required("collector")
def collector_update(cid):
    db = get_db()
    c = db.execute("SELECT * FROM complaints WHERE id=? AND collector_id=?", (cid, session["uid"])).fetchone()
    status = request.form.get("status")
    if not c or status not in ("In Progress", "Resolved"):
        flash("Invalid request.", "error"); return redirect(url_for("collector_dashboard"))
    db.execute("UPDATE complaints SET status=? WHERE id=?", (status, cid))
    if status == "Resolved":   # record the collected waste so statistics update
        try: kg = max(float(request.form.get("quantity_kg") or 0), 0)
        except ValueError: kg = 0
        db.execute("INSERT INTO waste_reports (category,quantity_kg,area,collected_on,collector_id) VALUES (?,?,?,?,?)",
                   (c["waste_type"], kg, c["location"], date.today().isoformat(), session["uid"]))
    db.commit(); flash(f"Complaint {complaint_id(cid)} marked {status}.", "success")
    return redirect(url_for("collector_dashboard"))

if __name__ == "__main__":
    app.run(debug=True)
