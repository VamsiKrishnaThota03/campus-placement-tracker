# Campus Placement Tracker

A Flask and PostgreSQL web app for tracking campus placement data, with interactive Plotly charts covering departments, companies and salaries.

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?logo=plotly&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?logo=bootstrap&logoColor=white)

## Overview

The project has two parts:

- **Web app** (`web/`): a Flask app with a login. It shows a placement dashboard, student and company tables, and an analysis page. Data comes from PostgreSQL through SQLAlchemy, is aggregated with pandas, and is rendered with Plotly.js.
- **Offline analysis script** (`src/analyze_placements.py`): queries a PostgreSQL database with psycopg2. It saves Matplotlib/Seaborn charts as PNG files and writes a multi-sheet Excel report. It uses the schema in `database/`.

## Features

- **Login and logout** with Flask-Login. Passwords are stored as Werkzeug hashes.
- **Dashboard** with per-department totals: offers, accepted offers and average package.
- **Students page**: each student's department, CGPA, number of offers and highest package
- **Companies page**: each company's industry, number of offers and average package
- **Analysis page** with key stats (total students, placed students, average package, placement rate) and these Plotly charts:
  - Salary distribution by department (box plot)
  - Placement trends: total vs. accepted offers by month
  - Department-wise placement rate
  - Industry-wise hiring (pie chart)
  - Monthly placement counts
- **Sample data seeding**: `web/init_db.py` creates the tables, an admin user, 4 departments, 4 companies, 20 students and 30 job offers.
- **Excel and PNG reports** from `src/analyze_placements.py`, with company, department, salary distribution and trend sheets.
- **SQL scripts** for creating the standalone schema and loading sample data or a larger dataset (`database/`).

## Tech stack

| Layer          | Technology                                         |
|----------------|----------------------------------------------------|
| Backend        | Python, Flask 2.3, Flask-SQLAlchemy, Flask-Login   |
| Database       | PostgreSQL (psycopg2)                              |
| Data           | pandas, Plotly (web), Matplotlib + Seaborn (script), openpyxl |
| Frontend       | Jinja2 templates, Bootstrap 5, Plotly.js (CDN)     |

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
│   ├── app.py                # Flask app, models, routes, chart queries
│   ├── init_db.py            # Drops, recreates and seeds the web app tables
│   ├── templates/            # base, index, login, dashboard, students, companies, analysis
│   └── static/css/style.css
└── requirements.txt
```

## Getting started

### Prerequisites

- Python 3.8+
- PostgreSQL

### Install

```bash
git clone https://github.com/VamsiKrishnaThota03/campus-placement-tracker.git
cd campus-placement-tracker
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment variables

Create a `.env` file in the project root. `python-dotenv` searches upward from the script directory, so it is found from both `web/` and `src/`.

| Variable      | Description                         | Example               |
|---------------|-------------------------------------|-----------------------|
| `DB_USER`     | PostgreSQL user                     | `<db_user>`           |
| `DB_PASSWORD` | PostgreSQL password (required)      | `<db_password>`       |
| `DB_HOST`     | Database host                       | `localhost`           |
| `DB_PORT`     | Database port                       | `5432`                |
| `DB_NAME`     | Database name                       | `placement_tracker`   |
| `SECRET_KEY`  | Flask session secret                | `<random-secret>`     |

### Initialize the database

Create the database (for example `createdb placement_tracker`), then:

```bash
cd web
python init_db.py
```

> `init_db.py` runs `db.drop_all()` first, so it wipes any existing web app tables.

### Run the web app

```bash
cd web
python app.py
```

Open <http://localhost:5001>. The seeded account is username `admin`, password `admin123`. Change it for anything beyond local use.

### Run the offline analysis (optional)

Load the standalone schema and sample data first, for example `psql -d placement_tracker -f database/setup_database.sql`. Then:

```bash
python src/analyze_placements.py
```

The script writes `company_placements.png`, `department_placements.png`, `salary_distribution.png` and `placement_analysis_<timestamp>.xlsx` to the current directory.

## Routes

| Method    | Path         | Auth     | Purpose                                 |
|-----------|--------------|----------|-----------------------------------------|
| GET       | `/`          | Public   | Landing page                            |
| GET, POST | `/login`     | Public   | Login form                              |
| GET       | `/logout`    | Required | Log out                                 |
| GET       | `/dashboard` | Required | Department statistics and charts        |
| GET       | `/students`  | Required | Student placement table                 |
| GET       | `/companies` | Required | Company hiring table                    |
| GET       | `/analysis`  | Required | Key statistics and Plotly charts        |
