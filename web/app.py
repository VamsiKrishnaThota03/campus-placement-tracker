from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
import json
from datetime import datetime
import urllib.parse

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

# Fix the database connection string
db_user = os.getenv('DB_USER')
db_password = urllib.parse.quote_plus(os.getenv('DB_PASSWORD'))  # URL encode the password
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model for authentication
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Department model
class Department(db.Model):
    dept_id = db.Column(db.Integer, primary_key=True)
    dept_name = db.Column(db.String(100), nullable=False)
    students = db.relationship('Student', backref='department', lazy=True)

# Student model
class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    dept_id = db.Column(db.Integer, db.ForeignKey('department.dept_id'), nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    job_offers = db.relationship('JobOffer', backref='student', lazy=True)

# Company model
class Company(db.Model):
    company_id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    job_offers = db.relationship('JobOffer', backref='company', lazy=True)

# Job Offer model
class JobOffer(db.Model):
    offer_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.company_id'), nullable=False)
    package_amount = db.Column(db.Float, nullable=False)
    offer_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_accepted = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get placement statistics
    stats = get_placement_statistics()
    plots = generate_analysis_plots()
    return render_template('dashboard.html', stats=stats, plots=plots)

@app.route('/companies')
@login_required
def companies():
    # Get company data
    companies = get_company_data()
    return render_template('companies.html', companies=companies)

@app.route('/students')
@login_required
def students():
    # Get student data
    students = get_student_data()
    return render_template('students.html', students=students)

@app.route('/analysis')
@login_required
def analysis():
    # Generate analysis plots
    plots = generate_analysis_plots()
    # Get key statistics
    stats = get_key_statistics()
    return render_template('analysis.html', plots=plots, stats=stats)

# Helper functions
def get_placement_statistics():
    query = """
    SELECT 
        d.dept_name,
        COUNT(jo.offer_id) as total_offers,
        COUNT(CASE WHEN jo.is_accepted THEN 1 END) as accepted_offers,
        AVG(jo.package_amount) as avg_package
    FROM department d
    LEFT JOIN student s ON d.dept_id = s.dept_id
    LEFT JOIN job_offer jo ON s.student_id = jo.student_id
    GROUP BY d.dept_name
    """
    df = pd.read_sql_query(query, db.engine)
    
    # Convert NumPy types to Python native types
    df['total_offers'] = df['total_offers'].astype(int)
    df['accepted_offers'] = df['accepted_offers'].astype(int)
    df['avg_package'] = df['avg_package'].astype(float)
    
    return df

def get_company_data():
    query = """
    SELECT 
        c.company_name,
        c.industry,
        COUNT(jo.offer_id) as total_offers,
        AVG(jo.package_amount) as avg_package
    FROM company c
    LEFT JOIN job_offer jo ON c.company_id = jo.company_id
    GROUP BY c.company_id, c.company_name, c.industry
    """
    df = pd.read_sql_query(query, db.engine)
    
    # Convert NumPy types to Python native types
    df['total_offers'] = df['total_offers'].astype(int)
    df['avg_package'] = df['avg_package'].astype(float)
    
    return df

def get_student_data():
    query = """
    SELECT 
        s.first_name,
        s.last_name,
        d.dept_name,
        s.cgpa,
        COUNT(jo.offer_id) as total_offers,
        MAX(jo.package_amount) as max_package
    FROM student s
    JOIN department d ON s.dept_id = d.dept_id
    LEFT JOIN job_offer jo ON s.student_id = jo.student_id
    GROUP BY s.student_id, s.first_name, s.last_name, d.dept_name, s.cgpa
    """
    df = pd.read_sql_query(query, db.engine)
    
    # Convert NumPy types to Python native types
    df['cgpa'] = df['cgpa'].astype(float)
    df['total_offers'] = df['total_offers'].astype(int)
    df['max_package'] = df['max_package'].astype(float)
    
    return df

def generate_analysis_plots():
    plots = {}
    
    # Salary distribution by department
    query = """
    SELECT 
        d.dept_name,
        jo.package_amount
    FROM job_offer jo
    JOIN student s ON jo.student_id = s.student_id
    JOIN department d ON s.dept_id = d.dept_id
    WHERE jo.is_accepted = true
    """
    df = pd.read_sql_query(query, db.engine)
    
    # Convert NumPy types to Python native types
    df['package_amount'] = df['package_amount'].astype(float)
    
    fig = px.box(df, x='dept_name', y='package_amount', title='Salary Distribution by Department')
    
    # Convert NumPy arrays to Python lists in the figure data
    fig_dict = fig.to_dict()
    for trace in fig_dict['data']:
        for key, value in trace.items():
            if hasattr(value, 'tolist'):
                trace[key] = value.tolist()
    
    plots['salary_dist'] = json.dumps(fig_dict)
    
    # Placement trends
    query = """
    SELECT 
        EXTRACT(MONTH FROM jo.offer_date) as month,
        COUNT(jo.offer_id) as total_offers,
        COUNT(CASE WHEN jo.is_accepted THEN 1 END) as accepted_offers
    FROM job_offer jo
    GROUP BY EXTRACT(MONTH FROM jo.offer_date)
    ORDER BY month
    """
    df = pd.read_sql_query(query, db.engine)
    
    # Convert NumPy types to Python native types
    df['month'] = df['month'].astype(int)
    df['total_offers'] = df['total_offers'].astype(int)
    df['accepted_offers'] = df['accepted_offers'].astype(int)
    
    fig = px.line(df, x='month', y=['total_offers', 'accepted_offers'], title='Placement Trends')
    
    # Convert NumPy arrays to Python lists in the figure data
    fig_dict = fig.to_dict()
    for trace in fig_dict['data']:
        for key, value in trace.items():
            if hasattr(value, 'tolist'):
                trace[key] = value.tolist()
    
    plots['placement_trends'] = json.dumps(fig_dict)
    
    # Department-wise placement rate
    query = """
    SELECT 
        d.dept_name,
        COUNT(CASE WHEN jo.is_accepted THEN 1 END)::FLOAT / COUNT(DISTINCT s.student_id) * 100 as placement_rate
    FROM department d
    LEFT JOIN student s ON d.dept_id = s.dept_id
    LEFT JOIN job_offer jo ON s.student_id = jo.student_id
    GROUP BY d.dept_name
    """
    df = pd.read_sql_query(query, db.engine)
    
    # Convert NumPy types to Python native types
    df['placement_rate'] = df['placement_rate'].astype(float)
    
    fig = px.bar(df, x='dept_name', y='placement_rate', title='Department-wise Placement Rate')
    
    # Convert NumPy arrays to Python lists in the figure data
    fig_dict = fig.to_dict()
    for trace in fig_dict['data']:
        for key, value in trace.items():
            if hasattr(value, 'tolist'):
                trace[key] = value.tolist()
    
    plots['dept_placement_rate'] = json.dumps(fig_dict)
    
    # Industry-wise hiring
    query = """
    SELECT 
        c.industry,
        COUNT(jo.offer_id) as total_offers
    FROM company c
    LEFT JOIN job_offer jo ON c.company_id = jo.company_id
    GROUP BY c.industry
    """
    df = pd.read_sql_query(query, db.engine)
    
    # Convert NumPy types to Python native types
    df['total_offers'] = df['total_offers'].astype(int)
    
    fig = px.pie(df, values='total_offers', names='industry', title='Industry-wise Hiring')
    
    # Convert NumPy arrays to Python lists in the figure data
    fig_dict = fig.to_dict()
    for trace in fig_dict['data']:
        for key, value in trace.items():
            if hasattr(value, 'tolist'):
                trace[key] = value.tolist()
    
    plots['industry_hiring'] = json.dumps(fig_dict)
    
    # Monthly trends
    query = """
    SELECT 
        EXTRACT(MONTH FROM jo.offer_date) as month,
        COUNT(jo.offer_id) as total_offers
    FROM job_offer jo
    GROUP BY EXTRACT(MONTH FROM jo.offer_date)
    ORDER BY month
    """
    df = pd.read_sql_query(query, db.engine)
    
    # Convert NumPy types to Python native types
    df['month'] = df['month'].astype(int)
    df['total_offers'] = df['total_offers'].astype(int)
    
    fig = px.bar(df, x='month', y='total_offers', title='Monthly Placement Trends')
    
    # Convert NumPy arrays to Python lists in the figure data
    fig_dict = fig.to_dict()
    for trace in fig_dict['data']:
        for key, value in trace.items():
            if hasattr(value, 'tolist'):
                trace[key] = value.tolist()
    
    plots['monthly_trends'] = json.dumps(fig_dict)
    
    return plots

def get_key_statistics():
    """Get key statistics for the analysis page"""
    # Total students
    query = """
    SELECT COUNT(*) as total_students
    FROM student
    """
    total_students = pd.read_sql_query(query, db.engine)['total_students'].iloc[0]
    
    # Placed students
    query = """
    SELECT COUNT(DISTINCT s.student_id) as placed_students
    FROM student s
    JOIN job_offer jo ON s.student_id = jo.student_id
    WHERE jo.is_accepted = true
    """
    placed_students = pd.read_sql_query(query, db.engine)['placed_students'].iloc[0]
    
    # Average package
    query = """
    SELECT AVG(jo.package_amount) as avg_package
    FROM job_offer jo
    WHERE jo.is_accepted = true
    """
    avg_package = pd.read_sql_query(query, db.engine)['avg_package'].iloc[0]
    
    # Placement rate
    placement_rate = (placed_students / total_students) * 100 if total_students > 0 else 0
    
    return {
        'total_students': total_students,
        'placed_students': placed_students,
        'avg_package': avg_package,
        'placement_rate': placement_rate
    }

def init_db():
    """Initialize the database with sample data"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if we already have data
        if User.query.count() > 0:
            print("Database already initialized with data")
            return
        
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
    app.run(debug=True, port=5001) 