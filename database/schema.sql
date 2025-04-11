-- Create database (run this separately in pgAdmin)
-- CREATE DATABASE placement_tracker;

-- Connect to the database
-- \c placement_tracker

-- Drop existing tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS placement_statistics;
DROP TABLE IF EXISTS job_offers;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS departments;

-- Create departments table
CREATE TABLE IF NOT EXISTS departments (
    dept_id SERIAL PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL,
    total_students INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create companies table
CREATE TABLE IF NOT EXISTS companies (
    company_id SERIAL PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    industry VARCHAR(100),
    company_size VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create students table
CREATE TABLE IF NOT EXISTS students (
    student_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    dept_id INTEGER REFERENCES departments(dept_id),
    cgpa DECIMAL(3,2),
    graduation_year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create job_offers table
CREATE TABLE IF NOT EXISTS job_offers (
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
CREATE TABLE IF NOT EXISTS placement_statistics (
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

-- Insert sample data for departments
INSERT INTO departments (dept_name, total_students) VALUES
('Computer Science', 120),
('Electronics', 100),
('Mechanical', 80),
('Civil', 60),
('Chemical', 40);

-- Insert sample data for companies
INSERT INTO companies (company_name, industry, company_size) VALUES
('TechCorp', 'Technology', 'Large'),
('DataSystems', 'Data Analytics', 'Medium'),
('BuildTech', 'Construction', 'Large'),
('ChemSolutions', 'Chemical', 'Medium'),
('AutoTech', 'Automotive', 'Large');

-- Insert sample data for students
INSERT INTO students (first_name, last_name, dept_id, cgpa, graduation_year) VALUES
('John', 'Doe', 1, 8.5, 2024),
('Jane', 'Smith', 1, 9.0, 2024),
('Mike', 'Johnson', 2, 8.2, 2024),
('Sarah', 'Williams', 3, 7.8, 2024),
('David', 'Brown', 4, 8.7, 2024);

-- Insert sample data for job offers
INSERT INTO job_offers (company_id, student_id, package_amount, job_role, location, offer_date, is_accepted) VALUES
(1, 1, 1200000.00, 'Software Engineer', 'Bangalore', '2024-01-15', true),
(2, 2, 1100000.00, 'Data Analyst', 'Hyderabad', '2024-01-20', true),
(3, 3, 900000.00, 'Mechanical Engineer', 'Chennai', '2024-01-25', false),
(4, 4, 850000.00, 'Chemical Engineer', 'Mumbai', '2024-02-01', true),
(5, 5, 950000.00, 'Civil Engineer', 'Delhi', '2024-02-05', true);

-- Insert sample data for placement statistics
INSERT INTO placement_statistics (dept_id, year, total_offers, accepted_offers, avg_package, max_package, min_package) VALUES
(1, 2024, 100, 95, 1150000.00, 1500000.00, 900000.00),
(2, 2024, 80, 75, 1000000.00, 1300000.00, 800000.00),
(3, 2024, 60, 55, 900000.00, 1200000.00, 700000.00),
(4, 2024, 45, 40, 850000.00, 1100000.00, 650000.00),
(5, 2024, 30, 28, 800000.00, 1000000.00, 600000.00); 