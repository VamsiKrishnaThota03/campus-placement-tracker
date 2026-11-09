"""Offline placement analysis against the PostgreSQL schema in database/.

Writes PNG charts and an Excel workbook to reports/ (or REPORTS_DIR).
"""
import os
import urllib.parse
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # no display needed
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / '.env')
REPORTS_DIR = Path(os.getenv('REPORTS_DIR', ROOT / 'reports'))


def analysis_database_url():
    """ANALYSIS_DATABASE_URL, else DATABASE_URL, else the DB_* variables."""
    url = os.getenv('ANALYSIS_DATABASE_URL') or os.getenv('DATABASE_URL')
    if url:
        return url.replace('postgres://', 'postgresql://', 1)
    if not os.getenv('DB_NAME'):
        raise SystemExit('Set ANALYSIS_DATABASE_URL, DATABASE_URL or DB_NAME/DB_USER/DB_PASSWORD/'
                         'DB_HOST/DB_PORT to point at the PostgreSQL database.')
    user = urllib.parse.quote_plus(os.getenv('DB_USER', ''))
    password = urllib.parse.quote_plus(os.getenv('DB_PASSWORD', ''))
    auth = f'{user}:{password}@' if password else (f'{user}@' if user else '')
    return (f"postgresql://{auth}{os.getenv('DB_HOST', 'localhost')}:"
            f"{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME')}")


@lru_cache(maxsize=1)
def get_engine():
    return create_engine(analysis_database_url())


def execute_query(query):
    """Execute a SQL query and return results as a pandas DataFrame"""
    return pd.read_sql_query(query, get_engine())

def analyze_company_wise_placements():
    """Analyze placement patterns by company"""
    query = """
    SELECT 
        c.company_name,
        c.industry,
        COUNT(jo.offer_id) as total_offers,
        COUNT(CASE WHEN jo.is_accepted THEN 1 END) as accepted_offers,
        AVG(jo.package_amount) as avg_package,
        MAX(jo.package_amount) as max_package
    FROM companies c
    LEFT JOIN job_offers jo ON c.company_id = jo.company_id
    GROUP BY c.company_id, c.company_name, c.industry
    ORDER BY total_offers DESC;
    """
    return execute_query(query)

def analyze_department_wise_placements():
    """Analyze placement patterns by department"""
    query = """
    SELECT 
        d.dept_name,
        d.total_students,
        COUNT(jo.offer_id) as total_offers,
        COUNT(CASE WHEN jo.is_accepted THEN 1 END) as accepted_offers,
        ROUND(COUNT(CASE WHEN jo.is_accepted THEN 1 END)::DECIMAL / d.total_students * 100, 2) as placement_percentage,
        AVG(jo.package_amount) as avg_package
    FROM departments d
    LEFT JOIN students s ON d.dept_id = s.dept_id
    LEFT JOIN job_offers jo ON s.student_id = jo.student_id
    GROUP BY d.dept_id, d.dept_name, d.total_students
    ORDER BY placement_percentage DESC;
    """
    return execute_query(query)

def analyze_salary_distribution():
    """Analyze salary distribution across departments"""
    query = """
    SELECT 
        d.dept_name,
        jo.package_amount,
        jo.job_role
    FROM job_offers jo
    JOIN students s ON jo.student_id = s.student_id
    JOIN departments d ON s.dept_id = d.dept_id
    WHERE jo.is_accepted = true;
    """
    return execute_query(query)

def analyze_placement_trends():
    """Analyze placement trends over time"""
    query = """
    SELECT 
        EXTRACT(MONTH FROM jo.offer_date) as month,
        COUNT(jo.offer_id) as total_offers,
        COUNT(CASE WHEN jo.is_accepted THEN 1 END) as accepted_offers,
        AVG(jo.package_amount) as avg_package
    FROM job_offers jo
    GROUP BY EXTRACT(MONTH FROM jo.offer_date)
    ORDER BY month;
    """
    return execute_query(query)

def generate_visualizations():
    """Generate visualizations for the analysis"""
    # Company-wise placements
    company_data = analyze_company_wise_placements()
    plt.figure(figsize=(12, 6))
    sns.barplot(data=company_data, x='company_name', y='total_offers')
    plt.title('Total Offers by Company')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / 'company_placements.png', dpi=120)
    plt.close()

    # Department-wise placement percentage
    dept_data = analyze_department_wise_placements()
    plt.figure(figsize=(10, 6))
    sns.barplot(data=dept_data, x='dept_name', y='placement_percentage')
    plt.title('Placement Percentage by Department')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / 'department_placements.png', dpi=120)
    plt.close()

    # Salary distribution
    salary_data = analyze_salary_distribution()
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=salary_data, x='dept_name', y='package_amount')
    plt.title('Salary Distribution by Department')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / 'salary_distribution.png', dpi=120)
    plt.close()

def generate_excel_report():
    """Generate comprehensive Excel report"""
    # Create Excel writer
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    excel_file = REPORTS_DIR / f'placement_analysis_{timestamp}.xlsx'
    writer = pd.ExcelWriter(excel_file, engine='openpyxl')

    # Write different analyses to different sheets
    analyze_company_wise_placements().to_excel(writer, sheet_name='Company Analysis', index=False)
    analyze_department_wise_placements().to_excel(writer, sheet_name='Department Analysis', index=False)
    analyze_salary_distribution().to_excel(writer, sheet_name='Salary Distribution', index=False)
    analyze_placement_trends().to_excel(writer, sheet_name='Placement Trends', index=False)

    # Save the Excel file
    writer.close()
    return excel_file

def main():
    """Main function to run the analysis"""
    try:
        print("Starting placement analysis...")
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Generate visualizations
        print("Generating visualizations...")
        generate_visualizations()
        
        # Generate Excel report
        print("Generating Excel report...")
        excel_file = generate_excel_report()
        
        print(f"Analysis complete! Excel report saved as: {excel_file}")
        print(f"Visualizations have been saved as PNG files in {REPORTS_DIR}.")

    except Exception as e:
        raise SystemExit(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 