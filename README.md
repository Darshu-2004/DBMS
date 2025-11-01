# TRANSIT — Transit System (DBMS project)

This repository contains a small transit management web application (Flask + Jinja templates) and a companion Streamlit view for quick inspection. It is intended for learning and demo purposes.

## Features
- User authentication (admin / operator / passenger)
- Role-specific dashboards and pages (users, stations, routes, vehicles, trips, tickets, payments, announcements)
- MySQL-backed schema (see `ddl.sql` / `dml.sql`)
- Redis-backed sessions when available, filesystem fallback for local dev

## Important note on passwords
> For this exercise the project stores passwords in plaintext (column `User.password_hash`) by design. THIS IS NOT SAFE FOR PRODUCTION. Before deploying, migrate to hashed passwords (bcrypt/argon2) and update the auth flow.

## Quickstart (development)

1) Create a virtual environment and install requirements

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash / WSL)
pip install -r requirements.txt
```

2) Configure environment variables (optional — defaults are provided)

- `MYSQL_HOST` (default: `localhost`)
- `MYSQL_USER` (default: `adminuser`)
- `MYSQL_PASSWORD` (default: `adminpassword`)
- `MYSQL_DB` (default: `transport`)
- `REDIS_HOST` (default: `localhost`)
- `REDIS_PORT` (default: `6379`)
- `SECRET_KEY` (recommended for session signing)
- `SHOW_SERVICE_BADGES` (true/false, default: true)

You can export these in your shell or set them in your development environment.

3) Initialize the database

Use the provided SQL files to create schema and sample data.

```bash
# Run the DDL to create tables
mysql -u root -p transport < ddl.sql
# Optionally load sample data
mysql -u root -p transport < dml.sql
```

If you need to inspect or normalize enum values, use the `SHOW COLUMNS` and `SELECT DISTINCT` queries. Do NOT attempt to add case-variant values to ENUMs (MySQL treats 'cash' and 'Cash' as duplicates under default collations and ALTER will fail). Instead normalize application data to canonical tokens.

Example normalization (run on a copy/backup first):

```sql
-- Backup first
CREATE TABLE Payment_backup AS SELECT * FROM Payment;

-- Normalize common display values to canonical enum tokens
UPDATE Payment
SET method = 'credit_card'
WHERE LOWER(TRIM(method)) IN ('credit card','creditcard','card','cc');

UPDATE Payment
SET method = 'debit_card'
WHERE LOWER(TRIM(method)) IN ('debit card','debitcard','debit');

UPDATE Payment
SET method = 'wallet'
WHERE LOWER(TRIM(method)) IN ('wallet','upi','netbanking');

UPDATE Payment
SET method = 'cash'
WHERE LOWER(TRIM(method)) = 'cash';
```

## Runtime (start the Flask app)

```bash
# From repo root
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Streamlit (optional)

There is a companion Streamlit app for quick inspection and dashboards. To run:

```bash
# from repo root
streamlit run streamlit_app.py
```

## Project layout
- `app.py` — Flask application and routes
- `templates/` — Jinja2 templates for UI
- `static/` — css and static assets
- `ddl.sql`, `dml.sql`, `user_create.sql`, `privileges.sql` — database schema and sample data
- `tools/` — utility scripts (e.g., `hash_plain_passwords.py`)

## Debugging tips
- The `/pay` handler logs the incoming form payload and the canonical values used for INSERT as:
  - `PAY POST payload: {...}`
  - `PAY INSERT values: ticket=... amount=... method=... status=...`
- If you see MySQL enum/truncation errors, reproduce the failing POST and inspect those logs — they reveal exactly what was sent and what the app tried to insert.

## Security and production notes
- Store hashed passwords (bcrypt/argon2) and never use plaintext in production.
- Use HTTPS, set a secure `SECRET_KEY`, and enable CSRF protection for forms.
- Consider running MySQL and Redis as managed services or in containers for reproducible environments.

## Committing & pushing
- Stage, commit, and push your branch (example):

```bash
git add -A
git commit -m "Fix: /pay normalization; add mapping and logging"
git push -u origin gui
```

If you prefer a pull request flow, create a feature branch and push that branch to GitHub.

## License
- This project is for educational/demo purposes. Replace with your preferred license if needed.

## Questions or next steps
- If you want, I can add a short migration script (SQL file) into `tools/` to normalize any historical values, or add a README section documenting how to migrate passwords to hashed values. Tell me which and I'll add it.
Streamlit conversion of Transit System

Run the Streamlit app (development):

1. Install requirements (recommended inside a venv):

```bash
pip install -r requirements.txt
```

2. Ensure your MySQL and Redis (if still used) servers are running and environment variables are set if you don't want to use defaults:

 - MYSQL_HOST (default: localhost)
 - MYSQL_USER (default: adminuser)
 - MYSQL_PASSWORD (default: adminpassword)
 - MYSQL_DB (default: transport)

3. Run Streamlit:

```bash
streamlit run streamlit_app.py
```

Notes
- The Streamlit app is a work-in-progress and provides core flows: login, dashboard, users, stations, routes, vehicles, trips, tickets, announcements, and payments.
- The app uses `pymysql` to talk to the same MySQL database your Flask app used. It expects the same schema.
- This initial conversion focuses on functionality and rapid iteration, not advanced security (password hashing, CSRF protection). Treat it as a dev/admin tool.
