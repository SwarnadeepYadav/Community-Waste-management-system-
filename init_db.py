"""Creates the SQLite database, all tables and sample data.
Run:  python init_db.py   (app.py also calls it automatically if the DB is missing)"""
import os, sqlite3, random
from datetime import date, timedelta
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "waste.db")

SCHEMA = """
DROP TABLE IF EXISTS complaints; DROP TABLE IF EXISTS waste_reports; DROP TABLE IF EXISTS schedules;
DROP TABLE IF EXISTS users; DROP TABLE IF EXISTS admins; DROP TABLE IF EXISTS collectors;

CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
  mobile TEXT NOT NULL, password TEXT NOT NULL, address TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE admins (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password TEXT NOT NULL);
CREATE TABLE collectors (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
  mobile TEXT NOT NULL, password TEXT NOT NULL, vehicle_no TEXT NOT NULL, area TEXT NOT NULL);
CREATE TABLE complaints (id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(id), waste_type TEXT NOT NULL, location TEXT NOT NULL,
  description TEXT NOT NULL, report_date TEXT NOT NULL, image TEXT,
  status TEXT NOT NULL DEFAULT 'Pending', collector_id INTEGER REFERENCES collectors(id),
  created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE waste_reports (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT NOT NULL, quantity_kg REAL NOT NULL,
  area TEXT NOT NULL, collected_on TEXT NOT NULL, collector_id INTEGER REFERENCES collectors(id));
CREATE TABLE schedules (id INTEGER PRIMARY KEY AUTOINCREMENT, area TEXT NOT NULL, waste_type TEXT NOT NULL,
  day TEXT NOT NULL, time TEXT NOT NULL, vehicle_no TEXT NOT NULL);
"""

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.executescript(SCHEMA)
    h = generate_password_hash
    db.execute("INSERT INTO admins (name,email,password) VALUES (?,?,?)", ("Admin", "admin@waste.com", h("admin123")))
    for c in [("Ravi Patil", "ravi@waste.com", "9876500001", "MH12-AB-1001", "Green Park"),
              ("Sunita Jadhav", "sunita@waste.com", "9876500002", "MH12-CD-2002", "Lake View"),
              ("Imran Shaikh", "imran@waste.com", "9876500003", "MH12-EF-3003", "Market Road")]:
        db.execute("INSERT INTO collectors (name,email,mobile,password,vehicle_no,area) VALUES (?,?,?,?,?,?)",
                   (c[0], c[1], c[2], h("collector123"), c[3], c[4]))
    for u in [("Asha Kulkarni", "user@example.com", "9123456780", "12, Green Park, Pune"),
              ("Rohan Mehta", "rohan@example.com", "9123456781", "45, Lake View, Pune")]:
        db.execute("INSERT INTO users (name,email,mobile,password,address) VALUES (?,?,?,?,?)",
                   (u[0], u[1], u[2], h("user123"), u[3]))
    today = date.today()
    sample = [  # user, type, location, description, days_ago, status, collector
        (1, "Plastic Waste", "Green Park Gate 2", "Plastic bottles piled near the gate.", 12, "Resolved", 1),
        (1, "Wet Waste", "Green Park Lane 4", "Food waste overflowing from the bin.", 9, "Resolved", 1),
        (2, "E-Waste", "Lake View Society", "Old monitors dumped on the roadside.", 7, "In Progress", 2),
        (2, "Dry Waste", "Lake View Garden", "Cardboard and paper scattered around.", 5, "Assigned", 2),
        (1, "Hazardous Waste", "Market Road Corner", "Broken tube lights and paint cans.", 4, "Assigned", 3),
        (2, "Other Waste", "Market Road Bus Stop", "Construction debris blocking the footpath.", 2, "Pending", None),
        (1, "Wet Waste", "Green Park Market", "Vegetable waste not collected for 3 days.", 1, "Pending", None),
        (2, "Plastic Waste", "Lake View Ground", "Plastic bags littered after an event.", 0, "Pending", None)]
    for s in sample:
        d = (today - timedelta(days=s[4])).isoformat()
        db.execute("INSERT INTO complaints (user_id,waste_type,location,description,report_date,status,collector_id) VALUES (?,?,?,?,?,?,?)",
                   (s[0], s[1], s[2], s[3], d, s[5], s[6]))
    for s in [("Green Park", "Wet Waste", "Monday", "07:00 AM", "MH12-AB-1001"), ("Green Park", "Dry Waste", "Thursday", "07:30 AM", "MH12-AB-1001"),
              ("Lake View", "Plastic Waste", "Tuesday", "08:00 AM", "MH12-CD-2002"), ("Lake View", "Wet Waste", "Saturday", "07:00 AM", "MH12-CD-2002"),
              ("Market Road", "E-Waste", "Wednesday", "10:00 AM", "MH12-EF-3003"), ("Market Road", "Hazardous Waste", "Friday", "11:00 AM", "MH12-EF-3003"),
              ("Market Road", "Dry Waste", "Sunday", "09:00 AM", "MH12-EF-3003")]:
        db.execute("INSERT INTO schedules (area,waste_type,day,time,vehicle_no) VALUES (?,?,?,?,?)", s)
    random.seed(7)
    base = {"Wet Waste": 420, "Dry Waste": 260, "Plastic Waste": 180, "E-Waste": 40, "Hazardous Waste": 25, "Other Waste": 90}
    for m in range(5, -1, -1):
        for cat, kg in base.items():
            when = (today - timedelta(days=30 * m + random.randint(0, 10))).isoformat()
            db.execute("INSERT INTO waste_reports (category,quantity_kg,area,collected_on,collector_id) VALUES (?,?,?,?,?)",
                       (cat, round(kg * random.uniform(0.8, 1.2), 1), random.choice(["Green Park", "Lake View", "Market Road"]), when, random.randint(1, 3)))
    db.commit(); db.close()

if __name__ == "__main__":
    init_db()
    print("Database created at", DB_PATH)
