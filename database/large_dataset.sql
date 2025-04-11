-- Start a transaction
BEGIN;

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

-- Insert departments data (10 departments)
INSERT INTO departments (dept_name, total_students) VALUES
('Computer Science', 200),
('Electronics', 180),
('Mechanical', 150),
('Civil', 120),
('Chemical', 100),
('Information Technology', 160),
('Aerospace', 80),
('Biotechnology', 90),
('Electrical', 140),
('Industrial', 110);

-- Insert companies data (20 companies)
INSERT INTO companies (company_name, industry, company_size) VALUES
('TechCorp', 'Technology', 'Large'),
('DataSystems', 'Data Analytics', 'Medium'),
('BuildTech', 'Construction', 'Large'),
('ChemSolutions', 'Chemical', 'Medium'),
('AutoTech', 'Automotive', 'Large'),
('AeroSpace', 'Aerospace', 'Large'),
('BioTech', 'Biotechnology', 'Medium'),
('PowerGrid', 'Electrical', 'Large'),
('IndTech', 'Industrial', 'Medium'),
('FinTech', 'Finance', 'Large'),
('CloudTech', 'Technology', 'Medium'),
('RoboTech', 'Robotics', 'Medium'),
('GreenEnergy', 'Energy', 'Large'),
('MedTech', 'Healthcare', 'Medium'),
('RetailTech', 'Retail', 'Large'),
('LogiTech', 'Logistics', 'Medium'),
('AgriTech', 'Agriculture', 'Medium'),
('EduTech', 'Education', 'Medium'),
('SecurityTech', 'Cybersecurity', 'Medium'),
('GameTech', 'Gaming', 'Medium');

-- Insert students data (500 students)
INSERT INTO students (first_name, last_name, dept_id, cgpa, graduation_year)
SELECT 
    'Student' || n as first_name,
    'LastName' || n as last_name,
    (n % 10) + 1 as dept_id,
    ROUND((7 + random() * 2.99)::numeric, 2) as cgpa,
    2024 as graduation_year
FROM generate_series(1, 500) n;

-- Insert job offers data (1000 offers)
INSERT INTO job_offers (company_id, student_id, package_amount, job_role, location, offer_date, is_accepted)
SELECT 
    (n % 20) + 1 as company_id,
    (n % 500) + 1 as student_id,
    (800000 + random() * 1200000)::numeric(10,2) as package_amount,
    CASE (n % 5)
        WHEN 0 THEN 'Software Engineer'
        WHEN 1 THEN 'Data Analyst'
        WHEN 2 THEN 'Research Engineer'
        WHEN 3 THEN 'Product Manager'
        ELSE 'Business Analyst'
    END as job_role,
    CASE (n % 5)
        WHEN 0 THEN 'Bangalore'
        WHEN 1 THEN 'Hyderabad'
        WHEN 2 THEN 'Mumbai'
        WHEN 3 THEN 'Delhi'
        ELSE 'Chennai'
    END as location,
    '2024-01-01'::date + (n % 90) as offer_date,
    random() > 0.2 as is_accepted
FROM generate_series(1, 1000) n;

-- Insert placement statistics data (10 departments * 3 years)
INSERT INTO placement_statistics (dept_id, year, total_offers, accepted_offers, avg_package, max_package, min_package)
SELECT 
    d.dept_id,
    y.year,
    COUNT(jo.offer_id) as total_offers,
    COUNT(CASE WHEN jo.is_accepted THEN 1 END) as accepted_offers,
    AVG(jo.package_amount) as avg_package,
    MAX(jo.package_amount) as max_package,
    MIN(jo.package_amount) as min_package
FROM departments d
CROSS JOIN (VALUES (2022), (2023), (2024)) as y(year)
LEFT JOIN students s ON d.dept_id = s.dept_id
LEFT JOIN job_offers jo ON s.student_id = jo.student_id
GROUP BY d.dept_id, y.year;

-- Commit the transaction
COMMIT; 