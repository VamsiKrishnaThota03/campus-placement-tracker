# Campus Placement Tracker

A comprehensive web application for tracking and analyzing campus placement data. This application helps educational institutions monitor placement statistics, manage student records, and analyze company hiring patterns.

## Features

- **User Authentication**: Secure login system with role-based access control
- **Interactive Dashboard**: Visual representation of placement statistics
- **Student Management**: Track student profiles, offers, and placement status
- **Company Information**: View company details and hiring patterns
- **Data Analysis**: Comprehensive analysis of placement trends and statistics
- **Responsive Design**: Mobile-friendly interface built with Bootstrap

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Data Visualization**: Plotly.js
- **Authentication**: Flask-Login

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL
- pip (Python package manager)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/campus-placement-tracker.git
   cd campus-placement-tracker
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   - Create a PostgreSQL database
   - Update the `.env` file with your database credentials

5. Initialize the database:
   ```
   python web/init_db.py
   ```

## Configuration

Create a `.env` file in the root directory with the following variables:

```
DB_USER=your_db_username
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=placement_tracker
SECRET_KEY=your-secret-key-here
```

## Usage

1. Start the application:
   ```
   cd web
   python app.py
   ```

2. Access the application at `http://localhost:5001`

3. Login with the default credentials:
   - Username: admin
   - Password: admin123

## Project Structure

```
campus-placement-tracker/
├── database/              # Database scripts
├── src/                   # Analysis scripts
├── web/                   # Web application
│   ├── static/            # Static files (CSS, JS)
│   ├── templates/         # HTML templates
│   ├── app.py             # Main application file
│   └── init_db.py         # Database initialization
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Bootstrap for the responsive UI components
- Plotly.js for interactive data visualizations
- Flask and its extensions for the web framework 