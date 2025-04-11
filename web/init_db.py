from app import app, db, User, Department, Company, Student, JobOffer
from datetime import datetime
import pandas as pd

def init_db():
    """Initialize the database with sample data"""
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create tables
        db.create_all()
        
        # Create admin user
        admin = User(username="admin", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        
        # Create departments
        departments = [
            Department(dept_name="Computer Science"),
            Department(dept_name="Electrical Engineering"),
            Department(dept_name="Mechanical Engineering"),
            Department(dept_name="Civil Engineering")
        ]
        db.session.add_all(departments)
        db.session.commit()
        
        # Create companies
        companies = [
            Company(company_name="TechCorp", industry="Technology"),
            Company(company_name="EngiSolutions", industry="Engineering"),
            Company(company_name="DataSystems", industry="Data Analytics"),
            Company(company_name="BuildRight", industry="Construction")
        ]
        db.session.add_all(companies)
        db.session.commit()
        
        # Create students
        students = []
        for i in range(1, 21):
            dept_id = (i % 4) + 1
            students.append(Student(
                first_name=f"Student{i}",
                last_name=f"LastName{i}",
                dept_id=dept_id,
                cgpa=7.5 + (i % 5) * 0.5
            ))
        db.session.add_all(students)
        db.session.commit()
        
        # Create job offers
        job_offers = []
        for i in range(1, 31):
            student_id = (i % 20) + 1
            company_id = (i % 4) + 1
            job_offers.append(JobOffer(
                student_id=student_id,
                company_id=company_id,
                package_amount=500000 + (i * 50000),
                offer_date=datetime(2023, 1, 1) + pd.Timedelta(days=i*10),
                is_accepted=(i % 3 != 0)
            ))
        db.session.add_all(job_offers)
        db.session.commit()
        
        print("Database initialized with sample data")

if __name__ == '__main__':
    init_db() 