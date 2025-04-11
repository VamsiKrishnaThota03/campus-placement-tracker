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