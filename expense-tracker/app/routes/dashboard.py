from flask import Blueprint, render_template, session, redirect, url_for
from app.models import User, Expense, Income, Budget
from app import db
from sqlalchemy import func, extract
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    # Check authentication
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        user_id = session['user_id']
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Safe queries with error handling
        try:
            total_expenses = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
                Expense.user_id == user_id,
                extract('month', Expense.date) == current_month,
                extract('year', Expense.date) == current_year
            ).scalar() or 0
        except:
            total_expenses = 0
            
        try:
            total_income = db.session.query(func.coalesce(func.sum(Income.amount), 0)).filter(
                Income.user_id == user_id,
                extract('month', Income.date) == current_month,
                extract('year', Income.date) == current_year
            ).scalar() or 0
        except:
            total_income = 0
            
        try:
            total_budget = db.session.query(func.coalesce(func.sum(Budget.amount), 0)).filter(
                Budget.user_id == user_id
            ).scalar() or 0
        except:
            total_budget = 0
        
        # Calculate derived values
        budget_remaining = max(0, float(total_budget) - float(total_expenses))
        savings = float(total_income) - float(total_expenses)
        
        # Get recent transactions
        try:
            recent_expenses = Expense.query.filter_by(user_id=user_id).order_by(
                Expense.date.desc()
            ).limit(5).all()
        except:
            recent_expenses = []
        
        return render_template('dashboard.html',
                             total_expenses=float(total_expenses),
                             total_income=float(total_income),
                             budget_remaining=budget_remaining,
                             savings=savings,
                             recent_expenses=recent_expenses)
                             
    except Exception as e:
        print(f"Dashboard error: {e}")
        # Return with default values if error occurs
        return render_template('dashboard.html',
                             total_expenses=0.0,
                             total_income=0.0,
                             budget_remaining=0.0,
                             savings=0.0,
                             recent_expenses=[])
