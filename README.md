# Community Waste Management System

Flask + SQLite + HTML/CSS/JavaScript project for managing community waste collection, complaints and awareness.

## How to run in VS Code
1. Install **Python 3.9+** (python.org) and **VS Code** with the *Python* extension.
2. Open VS Code → **File → Open Folder** → select the `waste_management` folder.
3. Open the terminal: **Terminal → New Terminal**.
4. (Recommended) create a virtual environment:
   - Windows: `python -m venv venv` then `venv\Scripts\activate`
   - Mac/Linux: `python3 -m venv venv` then `source venv/bin/activate`
5. Install Flask: `pip install -r requirements.txt`
6. (Optional) create/reset the database with sample data: `python init_db.py`
   (`app.py` also does this automatically if `database/waste.db` is missing.)
7. Start the server: `python app.py`
8. Open **http://127.0.0.1:5000** in your browser. Press `Ctrl+C` in the terminal to stop.

The statistics page loads Chart.js from the internet (cdnjs), so connect to the internet for the charts.

## Demo accounts
| Role | Email | Password |
|---|---|---|
| Resident | user@example.com | user123 |
| Admin | admin@waste.com | admin123 |
| Collector | ravi@waste.com | collector123 |

Suggested demo flow: log in as a resident → report waste → log in as admin → assign it to a collector → log in as collector → mark completed (enter kg) → check Statistics.

## Purpose of every file
| File | Purpose |
|---|---|
| `app.py` | Main Flask program: all pages (routes), login/session handling, image upload, search/filter, JSON API for charts |
| `init_db.py` | Creates the SQLite database, all 6 tables and sample data (users, admin, collectors, complaints, schedules, waste records) |
| `requirements.txt` | Python packages needed (Flask) |
| `database/waste.db` | The SQLite database file (created automatically) |
| `templates/base.html` | Common layout: navigation bar (changes by role), flash messages, footer |
| `templates/_filters.html` | Reusable search/filter bar (location, waste type, status, date) |
| `templates/index.html` | Home dashboard with statistic cards and upcoming collections |
| `templates/register.html`, `login.html` | Registration and login (resident / admin / collector) |
| `templates/report.html` | Form to report garbage with image upload |
| `templates/my_complaints.html` | Resident's complaint tracking table |
| `templates/categories.html` | The 6 waste categories and disposal methods |
| `templates/schedule.html` | Public collection schedule |
| `templates/awareness.html` | Reduce, Reuse, Recycle, segregation, composting, plastic reduction |
| `templates/statistics.html` | Four charts |
| `templates/admin.html` | Admin dashboard: stats, all complaints, change status, assign collector |
| `templates/admin_schedules.html` | Admin adds / edits / deletes schedules |
| `templates/admin_users.html` | Admin views users and collectors, adds collectors |
| `templates/admin_waste.html` | Admin views waste collection records |
| `templates/collector.html` | Collector's assigned complaints, map link, update status |
| `static/css/style.css` | All styling: green/white theme, cards, tables, responsive layout |
| `static/js/main.js` | Mobile menu, image preview, hiding messages |
| `static/js/charts.js` | Fetches `/api/stats` and draws charts using Chart.js |
| `static/uploads/` | Uploaded garbage images are stored here |

## Common problems
- `ModuleNotFoundError: flask` → run `pip install -r requirements.txt` (with the venv active).
- Want fresh data → delete `database/waste.db` and run `python init_db.py`.
- Port busy → change the last line of `app.py` to `app.run(debug=True, port=5001)`.
