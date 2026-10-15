# Community Waste Management System — Project Report

## 1. Abstract
Rapid urbanisation has increased the amount of waste produced by communities, while complaint handling and waste collection are still largely manual. The Community Waste Management System is a web application built with Python Flask, SQLite and HTML/CSS/JavaScript. Residents can register, report garbage problems with photos and track complaints. Administrators assign complaints to waste collectors, manage collection schedules and view statistics, and collectors update the status of their tasks. The system also teaches waste segregation and the 3Rs (Reduce, Reuse, Recycle), helping communities become cleaner and more sustainable.

## 2. Problem Statement
In many localities, residents do not know whom to complain to about uncollected or illegally dumped garbage, collection timings are not communicated, complaints are not tracked, and there is little awareness of segregation. Authorities have no central record of complaints or waste collected. A simple, transparent and accessible digital system is needed.

## 3. Objectives
- Provide an easy way to report garbage with location, description, date and image.
- Track every complaint through Pending → Assigned → In Progress → Resolved.
- Publish waste collection schedules for each area.
- Let the admin assign tasks to collectors and monitor performance.
- Record waste collected and present it as charts.
- Educate people about waste categories, disposal and the 3Rs.

## 4. Scope
**In scope:** resident, admin and collector roles; complaint lifecycle; schedules; statistics; awareness content; search/filter; responsive web interface; SQLite storage.
**Out of scope (current version):** SMS/email notifications, GPS live tracking, online payments, mobile native apps.

## 5. Features
Dashboard with live counts • Registration and secure login (hashed passwords) • Waste reporting with image upload • Six waste categories with disposal methods • Complaint tracking with IDs (WC-0001) • Collection schedule • Admin panel (view/assign/update complaints, manage schedules, view users, waste records) • Collector panel • Awareness section • Four charts • Search and filter by location, type, status, date • Responsive green/white UI.

## 6. Hardware and Software Requirements
**Hardware:** any PC/laptop with 4 GB RAM (8 GB recommended), 1 GHz+ processor, 500 MB free disk space.
**Software:** Windows/Linux/macOS, Python 3.9+, Flask 3, SQLite 3 (bundled with Python), VS Code, any modern browser (Chrome/Edge/Firefox), internet for Chart.js CDN.

## 7. System Architecture
A three-tier architecture:
1. **Presentation layer** – HTML templates (Jinja2), CSS and JavaScript in the browser.
2. **Application layer** – Flask (`app.py`) handles routes, validation, sessions, role-based access, file upload and JSON API.
3. **Data layer** – SQLite database `waste.db`.

Flow: Browser → HTTP request → Flask route → SQL query on SQLite → data returned → Jinja2 template renders HTML → Browser. Charts: `charts.js` calls `/api/stats` (JSON) and Chart.js draws the graphs.

## 8. Database / ER Diagram Description
Tables (PK = primary key, FK = foreign key):
- **users**(id PK, name, email unique, mobile, password, address, created_at)
- **admins**(id PK, name, email unique, password)
- **collectors**(id PK, name, email unique, mobile, password, vehicle_no, area)
- **complaints**(id PK, user_id FK→users, waste_type, location, description, report_date, image, status, collector_id FK→collectors, created_at)
- **waste_reports**(id PK, category, quantity_kg, area, collected_on, collector_id FK→collectors) — records of waste actually collected
- **schedules**(id PK, area, waste_type, day, time, vehicle_no)

Relationships: one **user** files many **complaints** (1:N); one **collector** is assigned many **complaints** (1:N) and creates many **waste_reports** (1:N); **admins** manage complaints and schedules; **schedules** are independent area-wise timetables.

```
USERS 1 ──< COMPLAINTS >── 1 COLLECTORS 1 ──< WASTE_REPORTS
ADMINS manage COMPLAINTS, SCHEDULES, COLLECTORS
```

## 9. Modules of the System
1. **Authentication module** – registration, login, logout, role checks.
2. **Complaint module** – report waste, upload image, track status.
3. **Category & awareness module** – categories, disposal methods, 3Rs.
4. **Schedule module** – view and manage collection timetable.
5. **Admin module** – complaint management, assignment, users, collectors, records.
6. **Collector module** – assigned tasks, location link, status update, kg entry.
7. **Statistics module** – JSON API and charts.
8. **Search & filter module** – location, type, status, date.

## 10. Future Scope
SMS/email/WhatsApp notifications • GPS/map-based location picking and live vehicle tracking • Mobile app • AI image classification of waste type • Reward points for segregation • Multi-city/ward support • PDF/Excel report export • Password reset by email • Deployment on cloud with PostgreSQL.

## 11. Advantages
Transparent complaint tracking • Faster response • Central digital record • Reduced paperwork • Promotes segregation and recycling • Simple, low-cost, runs on any laptop • Easy to extend • Mobile friendly.

## 12. Conclusion
The system shows how a simple web application can improve community waste handling by connecting residents, administrators and collectors. It improves accountability and awareness and can be scaled with notifications, GPS and analytics.

## 13. Viva Questions and Answers
1. **What is the aim of your project?** To help a community report waste problems, track their resolution, view collection schedules and learn proper segregation.
2. **Why Flask?** It is lightweight, easy for beginners, written in Python and needs little setup compared with Django.
3. **Why SQLite?** It is serverless, bundled with Python, stores data in one file and is ideal for small projects.
4. **How are passwords stored?** Hashed with Werkzeug's `generate_password_hash`; verified using `check_password_hash`. Plain passwords are never saved.
5. **How do you restrict pages by role?** A `login_required(role)` decorator checks the session role and redirects unauthorised users.
6. **What is a session?** Server-signed browser cookie storing the logged-in user's id, role and name, so they stay logged in between requests.
7. **How is the image upload handled?** Using `enctype="multipart/form-data"`; Flask receives it in `request.files`, the extension is checked, a random UUID filename is given and it is saved in `static/uploads`; only the filename goes in the database.
8. **How do you prevent SQL injection?** All queries use parameterised placeholders (`?`), never string concatenation of user input.
9. **Explain the complaint life cycle.** Pending (user submits) → Assigned (admin picks collector) → In Progress (collector starts) → Resolved (collector completes, kg recorded).
10. **How are charts created?** `/api/stats` returns grouped data as JSON using SQL `GROUP BY`; `charts.js` fetches it and Chart.js draws the graphs.
11. **What are the six waste categories?** Wet, Dry, Plastic, E-waste, Hazardous, Other.
12. **How is search/filter implemented?** The filter form sends GET parameters; Flask adds `AND ... LIKE/=` conditions to the SQL query.
13. **How is the design responsive?** CSS Grid with `auto-fit`, flexible tables with horizontal scroll, and media queries with a collapsible mobile menu.
14. **What is Jinja2?** Flask's template engine that inserts Python data into HTML using `{{ }}` and `{% %}`.
15. **What improvements would you add?** Notifications, GPS tracking, AI waste classification, cloud deployment.
16. **Difference between GET and POST?** GET requests data and shows it in the URL (filters); POST sends data in the body (forms, passwords).
17. **What is the ER relationship between users and complaints?** One-to-many: a user can file many complaints, each complaint belongs to one user.
