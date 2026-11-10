# Campus Placement Tracker

A Flask web app (PostgreSQL in production, SQLite for local development) for tracking campus placement data, with interactive Plotly charts covering departments, companies and salaries.

![Dashboard](docs/screenshots/dashboard.png)

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?logo=plotly&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?logo=bootstrap&logoColor=white)

[![CI](https://github.com/VamsiKrishnaThota03/campus-placement-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/VamsiKrishnaThota03/campus-placement-tracker/actions/workflows/ci.yml)
[![CodeQL](https://github.com/VamsiKrishnaThota03/campus-placement-tracker/actions/workflows/codeql.yml/badge.svg)](https://github.com/VamsiKrishnaThota03/campus-placement-tracker/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

The project has two parts:

- **Web app** (`web/`): a Flask app with a login. It shows a placement dashboard, student and company tables, and an analysis page. Data is read through SQLAlchemy (PostgreSQL or SQLite), aggregated with pandas, and rendered with Plotly.js.
- **Offline analysis script** (`src/analyze_placements.py`): queries a PostgreSQL database with psycopg2. It saves Matplotlib/Seaborn charts as PNG files and writes a multi-sheet Excel report. It uses the schema in `database/`.

## Features

- **Login and logout** with Flask-Login. Passwords are stored as Werkzeug hashes. Forms are CSRF-protected (Flask-WTF), logout is POST-only, and the post-login redirect only accepts local paths.
- **Dashboard**: summary cards (students, placed, placement rate, average accepted package), a per-department table (offers, accepted offers, share of students placed, average package), monthly placement trends and a package box plot by department.
- **Students page**: department, CGPA, number of offers, best package and a Placed / Offer pending / No offers badge, with instant search
- **Companies page**: industry, number of offers and average package, with instant search
- **Analysis page** with key stats and these Plotly charts:
  - Share of students placed per department
  - Accepted package distribution (histogram)
  - Offers by industry (donut)
  - Offers per month
- **Empty and error states**: charts and tables show a message when there is no data; custom 404/500 pages
- **Sample data seeding**: `flask --app app init-db` creates the tables, an admin user (password from `ADMIN_PASSWORD`), 4 departments, 4 companies, 20 students and 30 job offers.
- **Excel and PNG reports** from `src/analyze_placements.py`, with company, department, salary distribution and trend sheets.
- **SQL scripts** for creating the standalone schema and loading sample data or a larger dataset (`database/`).
- **Tests** (`web/test_app.py`) run against an in-memory SQLite database.

## Tech stack

| Layer          | Technology                                         |
|----------------|----------------------------------------------------|
| Backend        | Python, Flask 3.1, Flask-SQLAlchemy, Flask-Login, Flask-WTF (CSRF) |
| Database       | PostgreSQL (psycopg2) or SQLite for local development |
| Data           | pandas, Plotly (web), Matplotlib + Seaborn (script), openpyxl |
| Frontend       | Jinja2 templates, Bootstrap 5.3, Bootstrap Icons, Plotly.js 2.35 (CDN) |

## Project structure

```
campus-placement-tracker/
├── database/                 # SQL schema + sample data for the analysis script
│   ├── schema.sql
│   ├── create_tables.sql
│   ├── setup_database.sql
│   ├── insert_data.sql
│   └── large_dataset.sql
├── src/
│   └── analyze_placements.py # Generates PNG charts and an Excel report
├── web/
│   ├── app.py                # Flask app, models, routes, charts, `init-db` command
│   ├── init_db.py            # Drops, recreates and seeds the web app tables
│   ├── test_app.py           # unittest smoke tests
│   ├── templates/            # base, index, login, dashboard, students, companies, analysis, error
│   └── static/               # css/, js/ (chart rendering, table search), img/favicon.svg
├── docs/screenshots/
├── .env.example
└── requirements.txt
```

## Getting started

### Prerequisites

- Python 3.10+
- PostgreSQL for deployments (optional locally: without database settings the app uses `web/placements.db`, SQLite)

### Install

```bash
git clone https://github.com/VamsiKrishnaThota03/campus-placement-tracker.git
cd campus-placement-tracker
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then edit .env
```

### Environment variables

`.env` is read from the project root (or `web/`).

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | yes, unless `FLASK_DEBUG=1` | Flask session and CSRF signing key. Generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `FLASK_DEBUG` | no | `1` for local development only (enables the debugger and a throwaway secret key) |
| `DATABASE_URL` | no | e.g. `postgresql://user:pass@host:5432/placement_tracker`. `postgres://` URLs (Render, Heroku) are accepted. |
| `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` | no | Used instead of `DATABASE_URL` when `DB_NAME` is set |
| `ADMIN_USERNAME`, `ADMIN_PASSWORD` | for seeding | Account created by `flask --app app init-db` (username defaults to `admin`) |
| `PORT` | no | Port for `python app.py` (default `5001`) |
| `SESSION_COOKIE_SECURE` | no | Defaults to on when debug is off. Set `false` to test a non-debug build over plain HTTP. |
| `ANALYSIS_DATABASE_URL`, `REPORTS_DIR` | no | For `src/analyze_placements.py`; fall back to `DATABASE_URL` / `DB_*` and `reports/` |

With no database variables set, the web app uses SQLite at `web/placements.db`.

### Initialize the database

For PostgreSQL, create the database first (for example `createdb placement_tracker`). Then:

```bash
cd web
flask --app app init-db          # creates tables and sample data if the DB is empty
flask --app app init-db --reset  # drops all web-app tables first
```

`python init_db.py` does the same as `init-db --reset`.

### Run the web app

```bash
cd web
python app.py                    # http://127.0.0.1:5001
```

Log in with `ADMIN_USERNAME` / `ADMIN_PASSWORD`. For production, run it behind a WSGI server, e.g. `gunicorn app:app` from `web/`.

### Tests

```bash
cd web
python -m unittest -v
```

### Run the offline analysis (optional)

Load the standalone schema and sample data into PostgreSQL first, for example `psql -d placement_tracker -f database/setup_database.sql`. Then:

```bash
python src/analyze_placements.py
```

The script writes `company_placements.png`, `department_placements.png`, `salary_distribution.png` and `placement_analysis_<timestamp>.xlsx` to `reports/` (git-ignored).

## Routes

| Method    | Path         | Auth     | Purpose                                 |
|-----------|--------------|----------|-----------------------------------------|
| GET       | `/`          | Public   | Landing page                            |
| GET, POST | `/login`     | Public   | Login form                              |
| POST      | `/logout`    | Required | Log out                                 |
| GET       | `/dashboard` | Required | Department statistics and charts        |
| GET       | `/students`  | Required | Student placement table                 |
| GET       | `/companies` | Required | Company hiring table                    |
| GET       | `/analysis`  | Required | Key statistics and Plotly charts        |

## Screenshots

| Analysis | Students (mobile) |
|---|---|
| ![Analysis page](docs/screenshots/analysis.png) | <img src="docs/screenshots/students-mobile.png" alt="Students page on a phone" width="260"> |

## Known limitations

- The web app is read-only: data is loaded by the seed command or directly in the database. There are no forms to add students, companies or offers.
- `User.role` is stored but not checked; every logged-in user sees everything.
- The web app tables (`department`, `student`, `company`, `job_offer`) and the `database/*.sql` schema used by the analysis script (`departments`, `students`, …) are separate. The analysis script only works with PostgreSQL.
- There are no database migrations; `db.create_all()` creates missing tables but does not alter existing ones.
- `LICENSE` is empty.


## Security

The Flask configuration was already careful: `SECRET_KEY` has no production
fallback (the app raises unless `FLASK_DEBUG` is on), `CSRFProtect` is
registered, session and remember-me cookies are `HttpOnly`, `SameSite=Lax` and
`Secure` outside debug, and the dev server binds `127.0.0.1` by default.

What was missing was **response headers** — Flask sends none. An
`after_request` hook now adds a CSP, `nosniff`, `X-Frame-Options: DENY`, a
referrer policy, a `Permissions-Policy` denying camera/microphone/geolocation,
and HSTS (only when not in debug *and* secure cookies are on, so a plain-HTTP
deployment is not locked out of its own host for a year).

The CSP allows `cdn.jsdelivr.net` and `cdn.plot.ly`, which the templates load
Bootstrap, Bootstrap Icons and Plotly from, and permits `'unsafe-inline'` for
scripts and styles — Plotly injects inline style attributes and some templates
carry inline chart-initialisation blocks. That exception is named rather than
quietly omitted; removing it would mean vendoring those assets locally and
moving the inline blocks into files.

## Tests

```bash
python -m pytest web/test_app.py -v      # 13 tests
```

The 7 existing tests cover the dashboard, login and the statistics helpers. The
6 added cover the headers themselves — they produce no visible symptom when
they go missing, so a refactor can drop them silently — including that the CSP
still names both CDNs (forgetting one would break every chart in the browser
rather than failing server-side), that framing/objects/base-URI rewrites are
denied, and that HSTS is *not* announced from a plain-HTTP server.

Two more re-enable `CSRFProtect` (the other suites disable it so they can post
forms, which would otherwise make the protection untested) and assert the login
form carries a token and that a tokenless POST is rejected with 400 rather than
logging in.

## Continuous integration

| Job | What it proves |
| --- | --- |
| `test` (Python 3.11, 3.12) | The 13 tests |
| `config-safety` | Importing the app without `SECRET_KEY` raises instead of using a default; the running server listens on `127.0.0.1` and not `0.0.0.0` (read from `ss -ltn`); and the security headers are present on a real HTTP response, not only in tests |
| `docker` | The image builds |

CodeQL runs over Python weekly and on every push; Dependabot watches pip,
Actions and the Dockerfile.

## Docker

```bash
printf 'SECRET_KEY=%s\nPOSTGRES_PASSWORD=%s\nADMIN_PASSWORD=%s\n' \
  "$(python3 -c 'import secrets;print(secrets.token_hex(32))')" \
  "$(openssl rand -hex 16)" "$(openssl rand -base64 18)" > .env

docker compose up --build
open http://localhost:5001
```

Runs under gunicorn as a non-root user with PostgreSQL. Both ports publish to
`127.0.0.1` only, and Compose fails fast with a named error if any of the three
secrets is missing.
