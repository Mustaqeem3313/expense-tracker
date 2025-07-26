# Expense Tracker Application

A comprehensive personal finance management web application built with Flask, featuring expense tracking, budgeting, income management, and financial reporting.

## Features

- **User Authentication**: Secure login/register system
- **Dashboard**: Overview of financial status with key metrics
- **Expense Management**: Track daily expenses with categories
- **Income Tracking**: Record income from multiple sources
- **Budget Planning**: Set and monitor monthly budgets
- **Investment Portfolio**: Track investment performance
- **Financial Reports**: Generate PDF reports with charts
- **Settings**: Customize preferences and account settings

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript
- **Backend**: Python Flask with SQLAlchemy ORM
- **Database**: SQLite3
- **Reports**: ReportLab for PDF generation
- **Charts**: Chart.js for data visualization

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd expense-tracker
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## Default Login Credentials

- **Username**: admin@example.com
- **Password**: admin123

## Project Structure

```
expense-tracker/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── utils.py             # Utility functions
│   ├── static/              # CSS, JS, images
│   ├── templates/           # HTML templates
│   └── routes/              # Route blueprints
├── run.py                   # Application entry point
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
└── README.md               # Project documentation
```

## Usage

1. **Register** a new account or login with existing credentials
2. **Dashboard** provides overview of your financial status
3. **Add expenses** with date, amount, category, and description
4. **Track income** from various sources
5. **Set budgets** for different categories and monitor progress
6. **Generate reports** for monthly/quarterly analysis
7. **Manage investments** and track portfolio performance

## License

This project is licensed under the MIT License.
