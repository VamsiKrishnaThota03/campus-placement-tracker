-- Drop existing tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS placement_statistics CASCADE;
DROP TABLE IF EXISTS job_offers CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS companies CASCADE;
DROP TABLE IF EXISTS departments CASCADE;

-- Create departments table
CREATE TABLE departments (
    dept_id SERIAL PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL,
    total_students INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create companies table
CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    industry VARCHAR(100),
    company_size VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create students table
CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    dept_id INTEGER REFERENCES departments(dept_id),
    cgpa DECIMAL(3,2),
    graduation_year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create job_offers table
CREATE TABLE job_offers (
    offer_id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(company_id),
    student_id INTEGER REFERENCES students(student_id),
    package_amount DECIMAL(10,2),
    job_role VARCHAR(200),
    location VARCHAR(200),
    offer_date DATE,
    is_accepted BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create placement_statistics table
CREATE TABLE placement_statistics (
    stat_id SERIAL PRIMARY KEY,
    dept_id INTEGER REFERENCES departments(dept_id),
    year INTEGER,
    total_offers INTEGER,
    accepted_offers INTEGER,
    avg_package DECIMAL(10,2),
    max_package DECIMAL(10,2),
    min_package DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_students_dept ON students(dept_id);
CREATE INDEX idx_job_offers_company ON job_offers(company_id);
CREATE INDEX idx_job_offers_student ON job_offers(student_id);
CREATE INDEX idx_placement_stats_dept ON placement_statistics(dept_id); 