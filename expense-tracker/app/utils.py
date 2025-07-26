from datetime import datetime, timedelta
from functools import wraps
from flask import session, redirect, url_for, flash
import calendar

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def format_currency(amount, currency='USD'):
    """Format amount as currency"""
    symbol_map = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'INR': '₹',
        'CAD': 'C$',
        'AUD': 'A$'
    }
    symbol = symbol_map.get(currency, '$')
    return f"{symbol}{amount:,.2f}"

def get_month_name(month_num):
    """Get month name from month number"""
    return calendar.month_name[month_num]

def get_date_range(period='current_month'):
    """Get start and end dates for different periods"""
    today = datetime.now().date()

    if period == 'current_month':
        start = today.replace(day=1)
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

    elif period == 'last_month':
        if today.month == 1:
            start = today.replace(year=today.year - 1, month=12, day=1)
            end = today.replace(day=1) - timedelta(days=1)
        else:
            start = today.replace(month=today.month - 1, day=1)
            end = today.replace(day=1) - timedelta(days=1)

    elif period == 'current_quarter':
        current_quarter = (today.month - 1) // 3 + 1
        start = today.replace(month=(current_quarter - 1) * 3 + 1, day=1)
        if current_quarter == 4:
            end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = today.replace(month=current_quarter * 3 + 1, day=1) - timedelta(days=1)

    elif period == 'current_year':
        start = today.replace(month=1, day=1)
        end = today.replace(month=12, day=31)

    else:  # custom or default to current month
        start = today.replace(day=1)
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

    return start, end

def calculate_savings_rate(income, expenses):
    """Calculate savings rate as percentage"""
    if income == 0:
        return 0
    return ((income - expenses) / income) * 100

def get_expense_categories():
    """Get list of expense categories"""
    return [
        'Groceries',
        'Utilities',
        'Entertainment',
        'Transportation',
        'Healthcare',
        'Education',
        'Shopping',
        'Dining',
        'Travel',
        'Insurance',
        'Other'
    ]

def get_income_sources():
    """Get list of income sources"""
    return [
        'Salary',
        'Freelance',
        'Investment',
        'Business',
        'Rental',
        'Gift',
        'Other'
    ]

def get_investment_types():
    """Get list of investment types"""
    return [
        'Stocks',
        'Bonds',
        'Mutual Funds',
        'ETF',
        'Cryptocurrency',
        'Real Estate',
        'Commodities',
        'Other'
    ]

def validate_amount(amount_str):
    """Validate and convert amount string to float"""
    try:
        amount = float(amount_str)
        if amount < 0:
            return None, "Amount cannot be negative"
        if amount > 1000000:  # 1 million limit
            return None, "Amount is too large"
        return amount, None
    except (ValueError, TypeError):
        return None, "Invalid amount format"

def generate_report_filename(report_type, period, user_id):
    """Generate filename for reports"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{report_type}_{period}_{user_id}_{timestamp}.pdf"

class DateHelper:
    """Helper class for date operations"""

    @staticmethod
    def get_months_between(start_date, end_date):
        """Get list of months between two dates"""
        months = []
        current = start_date.replace(day=1)
        end = end_date.replace(day=1)

        while current <= end:
            months.append(current)
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        return months

    @staticmethod
    def get_week_start_end(date):
        """Get start and end of week for given date"""
        start = date - timedelta(days=date.weekday())
        end = start + timedelta(days=6)
        return start, end
