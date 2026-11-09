"""Campus Placement Tracker - Flask web app."""
import json
import os
import secrets
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path

import click
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (LoginManager, UserMixin, current_user, login_required, login_user,
                         logout_user)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / '.env')
load_dotenv(BASE_DIR / '.env')


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


def database_url():
    """DATABASE_URL, else DB_USER/DB_PASSWORD/DB_HOST/DB_PORT/DB_NAME, else a local SQLite file."""
    url = os.getenv('DATABASE_URL')
    if url:
        # Render/Heroku style URLs use the deprecated "postgres://" scheme.
        return url.replace('postgres://', 'postgresql://', 1)
    if os.getenv('DB_NAME'):
        user = urllib.parse.quote_plus(os.getenv('DB_USER', ''))
        password = urllib.parse.quote_plus(os.getenv('DB_PASSWORD', ''))
        auth = f'{user}:{password}@' if password else (f'{user}@' if user else '')
        host = os.getenv('DB_HOST', 'localhost')
        port = os.getenv('DB_PORT', '5432')
        return f"postgresql://{auth}{host}:{port}/{os.getenv('DB_NAME')}"
    # Local development fallback; no credentials involved.
    return f"sqlite:///{BASE_DIR / 'placements.db'}"


DEBUG = env_bool('FLASK_DEBUG', False)
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    if not DEBUG:
        raise RuntimeError('SECRET_KEY is not set. Set it in the environment or .env '
                           '(or set FLASK_DEBUG=1 for local development).')
    # Local development only: a random key per process (sessions reset on restart).
    SECRET_KEY = secrets.token_hex(32)

app = Flask(__name__)
app.config.update(
    SECRET_KEY=SECRET_KEY,
    SQLALCHEMY_DATABASE_URI=database_url(),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=env_bool('SESSION_COOKIE_SECURE', not DEBUG),
    REMEMBER_COOKIE_SECURE=env_bool('SESSION_COOKIE_SECURE', not DEBUG),
)

db = SQLAlchemy(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


# --------------------------------------------------------------------------- models

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Department(db.Model):
    dept_id = db.Column(db.Integer, primary_key=True)
    dept_name = db.Column(db.String(100), nullable=False)
    students = db.relationship('Student', backref='department', lazy=True)


class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    dept_id = db.Column(db.Integer, db.ForeignKey('department.dept_id'), nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    job_offers = db.relationship('JobOffer', backref='student', lazy=True)


class Company(db.Model):
    company_id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(100), nullable=False)
    job_offers = db.relationship('JobOffer', backref='company', lazy=True)


class JobOffer(db.Model):
    offer_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.company_id'), nullable=False)
    package_amount = db.Column(db.Float, nullable=False)
    offer_date = db.Column(db.DateTime, nullable=False,
                           default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    is_accepted = db.Column(db.Boolean, default=False)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# --------------------------------------------------------------------------- template helpers

@app.template_filter('inr')
def format_inr(value):
    """Format a rupee amount as lakhs, e.g. 1250000 -> '₹12.50 L'. Missing values -> '—'."""
    if value is None or pd.isna(value):
        return '—'
    return f'₹{value / 100_000:,.2f} L'


@app.context_processor
def inject_now():
    return {'current_year': datetime.now().year}


# --------------------------------------------------------------------------- data access
# Aggregation is done in pandas so the same code works on PostgreSQL and SQLite.

def _frame(statement):
    return pd.read_sql(statement, db.engine)


def offers_frame():
    """One row per job offer with student, department and company details."""
    stmt = (db.select(JobOffer.offer_id, JobOffer.package_amount, JobOffer.offer_date,
                      JobOffer.is_accepted, Student.student_id, Department.dept_name,
                      Company.company_name, Company.industry)
            .join(Student, JobOffer.student_id == Student.student_id)
            .join(Department, Student.dept_id == Department.dept_id)
            .join(Company, JobOffer.company_id == Company.company_id))
    df = _frame(stmt)
    df['is_accepted'] = df['is_accepted'].fillna(False).astype(bool)
    df['package_amount'] = df['package_amount'].astype(float)
    df['offer_date'] = pd.to_datetime(df['offer_date'])
    return df


def students_frame():
    stmt = (db.select(Student.student_id, Student.first_name, Student.last_name, Student.cgpa,
                      Department.dept_name)
            .join(Department, Student.dept_id == Department.dept_id))
    return _frame(stmt)


def get_placement_statistics():
    """Per-department offers, accepted offers, placement rate and average package."""
    departments = _frame(db.select(Department.dept_name).order_by(Department.dept_name))
    students = students_frame()
    offers = offers_frame()
    rows = []
    for name in departments['dept_name']:
        dept_offers = offers[offers['dept_name'] == name]
        dept_students = students[students['dept_name'] == name]
        accepted = dept_offers[dept_offers['is_accepted']]
        placed = accepted['student_id'].nunique()
        rows.append({
            'dept_name': name,
            'students': len(dept_students),
            'total_offers': len(dept_offers),
            'accepted_offers': len(accepted),
            'placed_students': placed,
            # Share of the department's students with at least one accepted offer.
            'placement_rate': (placed / len(dept_students) * 100) if len(dept_students) else 0.0,
            'avg_package': dept_offers['package_amount'].mean() if len(dept_offers) else None,
        })
    return pd.DataFrame(rows, columns=['dept_name', 'students', 'total_offers', 'accepted_offers',
                                       'placed_students', 'placement_rate', 'avg_package'])


def get_company_data():
    companies = _frame(db.select(Company.company_id, Company.company_name, Company.industry))
    offers = _frame(db.select(JobOffer.company_id, JobOffer.package_amount))
    grouped = offers.groupby('company_id')['package_amount'].agg(['count', 'mean']).reset_index()
    df = companies.merge(grouped, on='company_id', how='left')
    df['total_offers'] = df['count'].fillna(0).astype(int)
    df['avg_package'] = df['mean']
    return df.sort_values(['total_offers', 'company_name'], ascending=[False, True])


def get_student_data():
    students = students_frame()
    offers = _frame(db.select(JobOffer.student_id, JobOffer.package_amount, JobOffer.is_accepted))
    offers['is_accepted'] = offers['is_accepted'].fillna(False).astype(bool)
    grouped = offers.groupby('student_id').agg(
        total_offers=('package_amount', 'count'),
        max_package=('package_amount', 'max'),
        placed=('is_accepted', 'any'),
    ).reset_index()
    df = students.merge(grouped, on='student_id', how='left')
    df['total_offers'] = df['total_offers'].fillna(0).astype(int)
    df['placed'] = df['placed'].fillna(False).astype(bool)
    return df.sort_values(['dept_name', 'student_id'])


def get_key_statistics():
    students = students_frame()
    offers = offers_frame()
    accepted = offers[offers['is_accepted']]
    total = len(students)
    placed = accepted['student_id'].nunique()
    return {
        'total_students': total,
        'placed_students': placed,
        'total_offers': len(offers),
        'avg_package': accepted['package_amount'].mean() if len(accepted) else None,
        'max_package': offers['package_amount'].max() if len(offers) else None,
        'placement_rate': (placed / total * 100) if total else 0.0,
    }


# --------------------------------------------------------------------------- charts

PALETTE = ['#4f46e5', '#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#14b8a6']


def _figure(fig):
    """Plotly figure -> plain dict (embedded in templates with |tojson)."""
    fig.update_layout(
        template='plotly_white', colorway=PALETTE, title=None,
        margin=dict(t=24, r=16, b=48, l=56),
        font=dict(family='Inter, system-ui, sans-serif', color='#334155'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, title=None),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
    )
    fig.update_yaxes(rangemode='tozero', gridcolor='#e2e8f0')
    return json.loads(fig.to_json())


def generate_analysis_plots():
    """Return {name: figure dict or None}. None means there is no data to plot."""
    offers = offers_frame()
    accepted = offers[offers['is_accepted']]
    plots = dict.fromkeys(['salary_dist', 'placement_trends', 'dept_placement_rate',
                           'package_distribution', 'industry_hiring', 'monthly_trends'])

    if not accepted.empty:
        lakhs = accepted.assign(package_lakhs=accepted['package_amount'] / 100_000)
        fig = px.box(lakhs, x='dept_name', y='package_lakhs', color='dept_name', points='all',
                     labels={'dept_name': 'Department', 'package_lakhs': 'Package (₹ lakhs)'})
        fig.update_layout(showlegend=False)
        plots['salary_dist'] = _figure(fig)

        fig = px.histogram(lakhs, x='package_lakhs', nbins=12,
                           labels={'package_lakhs': 'Package (₹ lakhs)'})
        fig.update_traces(marker_line_color='white', marker_line_width=1)
        fig.update_layout(yaxis_title='Accepted offers', bargap=0.05)
        plots['package_distribution'] = _figure(fig)

    if not offers.empty:
        monthly = (offers.assign(month=offers['offer_date'].dt.to_period('M').dt.to_timestamp())
                   .groupby('month')
                   .agg(total_offers=('offer_id', 'count'), accepted_offers=('is_accepted', 'sum'))
                   .reset_index())
        fig = px.line(monthly, x='month', y=['total_offers', 'accepted_offers'], markers=True,
                      labels={'month': 'Month', 'value': 'Offers', 'variable': ''})
        names = {'total_offers': 'All offers', 'accepted_offers': 'Accepted'}
        fig.for_each_trace(lambda t: t.update(name=names.get(t.name, t.name)))
        fig.update_xaxes(dtick='M1', tickformat='%b %Y')
        plots['placement_trends'] = _figure(fig)

        fig = px.bar(monthly, x='month', y='total_offers',
                     labels={'month': 'Month', 'total_offers': 'Offers'})
        fig.update_xaxes(dtick='M1', tickformat='%b %Y')
        plots['monthly_trends'] = _figure(fig)

        industry = offers.groupby('industry').size().reset_index(name='total_offers')
        fig = px.pie(industry, values='total_offers', names='industry', hole=0.45)
        plots['industry_hiring'] = _figure(fig)

    stats = get_placement_statistics()
    if not stats.empty and stats['students'].sum() > 0:
        fig = px.bar(stats, x='dept_name', y='placement_rate',
                     labels={'dept_name': 'Department', 'placement_rate': 'Students placed (%)'})
        fig.update_yaxes(range=[0, 115])
        fig.update_traces(texttemplate='%{y:.0f}%', textposition='outside', cliponaxis=False)
        plots['dept_placement_rate'] = _figure(fig)

    return plots


# --------------------------------------------------------------------------- routes

def _safe_next(target):
    """Only allow same-site relative redirects after login."""
    if not target or not target.startswith('/') or target.startswith('//'):
        return None
    parts = urllib.parse.urlsplit(target)
    if parts.scheme or parts.netloc or '\\' in target:
        return None
    return target


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
        if user and user.check_password(password):
            login_user(user)
            return redirect(_safe_next(request.args.get('next')) or url_for('dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', stats=get_placement_statistics(),
                           summary=get_key_statistics(), plots=generate_analysis_plots())


@app.route('/companies')
@login_required
def companies():
    return render_template('companies.html', companies=get_company_data())


@app.route('/students')
@login_required
def students():
    return render_template('students.html', students=get_student_data())


@app.route('/analysis')
@login_required
def analysis():
    return render_template('analysis.html', plots=generate_analysis_plots(),
                           stats=get_key_statistics())


@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', code=404, message='Page not found.'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('error.html', code=500,
                           message='Something went wrong. Please try again.'), 500


# --------------------------------------------------------------------------- seeding

def seed_sample_data(reset=False):
    """Create tables and load sample data. Requires ADMIN_PASSWORD in the environment."""
    admin_password = os.getenv('ADMIN_PASSWORD')
    if not admin_password:
        raise click.ClickException('Set ADMIN_PASSWORD (and optionally ADMIN_USERNAME) '
                                   'before seeding the database.')
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')

    if reset:
        db.drop_all()
    db.create_all()

    if db.session.execute(db.select(db.func.count(User.id))).scalar():
        click.echo('Database already contains data; nothing to do (use --reset to start over).')
        return

    admin = User(username=admin_username, role='admin')
    admin.set_password(admin_password)
    db.session.add(admin)

    departments = [Department(dept_name=name) for name in (
        'Computer Science', 'Electrical Engineering', 'Mechanical Engineering', 'Civil Engineering')]
    companies = [
        Company(company_name='TechCorp', industry='Technology'),
        Company(company_name='EngiSolutions', industry='Engineering'),
        Company(company_name='DataSystems', industry='Data Analytics'),
        Company(company_name='BuildRight', industry='Construction'),
    ]
    db.session.add_all(departments + companies)
    db.session.flush()

    students = [Student(first_name=f'Student{i}', last_name=f'LastName{i}',
                        dept_id=departments[i % 4].dept_id, cgpa=7.5 + (i % 5) * 0.5)
                for i in range(1, 21)]
    db.session.add_all(students)
    db.session.flush()

    db.session.add_all([
        JobOffer(student_id=students[i % 20].student_id,
                 company_id=companies[i % 4].company_id,
                 package_amount=500000 + (i * 50000),
                 offer_date=datetime(2023, 1, 1) + timedelta(days=i * 10),
                 is_accepted=(i % 3 != 0))
        for i in range(1, 31)
    ])
    db.session.commit()
    click.echo(f"Database initialised with sample data. Log in as '{admin_username}'.")


@app.cli.command('init-db')
@click.option('--reset', is_flag=True, help='Drop all tables first (deletes existing data).')
def init_db_command(reset):
    """Create tables and load sample data."""
    seed_sample_data(reset=reset)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Loopback by default; set HOST only when a reverse proxy needs another interface.
    app.run(host=os.getenv('HOST', '127.0.0.1'), port=int(os.getenv('PORT', '5001')), debug=DEBUG)
