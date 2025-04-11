# Campus Placement Tracker

A comprehensive system for analyzing and tracking campus placement data using PostgreSQL, Python, and Excel.

## Features

- Database schema for storing placement data
- SQL queries for analyzing placement patterns
- Python scripts for data analysis and report generation
- Automated Excel report generation with visualizations

## Setup Instructions

1. Install PostgreSQL and pgAdmin if not already installed
2. Create a new database in pgAdmin
3. Run the SQL script in `database/schema.sql` to create the necessary tables
4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Create a `.env` file with your database credentials:
   ```
   DB_HOST=localhost
   DB_NAME=placement_tracker
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_PORT=5432
   ```
6. Run the data analysis script:
   ```bash
   python src/analyze_placements.py
   ```

## Project Structure

```
campus-placement-tracker/
├── database/
│   └── schema.sql
├── src/
│   ├── analyze_placements.py
│   └── generate_report.py
├── requirements.txt
└── README.md
```

## Database Schema

The database includes tables for:
- Students
- Companies
- Job Offers
- Departments
- Placement Statistics

## Analysis Features

- Company-wise hiring patterns
- Department-wise placement ratios
- Salary distribution analysis
- Offer acceptance rates
- Placement trends over time 