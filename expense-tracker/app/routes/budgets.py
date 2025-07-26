from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.models import Budget, Expense
from app import db
from sqlalchemy import func

budgets_bp = Blueprint('budgets', __name__)

@budgets_bp.route('/budgets', methods=['GET', 'POST'])
def budgets():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        try:
            # Check if budget already exists for this category
            existing_budget = Budget.query.filter_by(
                user_id=session['user_id'],
                category=request.form['category']
            ).first()
            
            if existing_budget:
                # Update existing budget
                existing_budget.amount = float(request.form['amount'])
                existing_budget.period = request.form['period']
                flash('Budget updated successfully!', 'success')
            else:
                # Create new budget
                budget = Budget(
                    user_id=session['user_id'],
                    category=request.form['category'],
                    amount=float(request.form['amount']),
                    period=request.form['period']
                )
                db.session.add(budget)
                flash('Budget set successfully!', 'success')
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            print(f"Budget creation error: {e}")
            flash('Error setting budget. Please try again.', 'error')
        
        return redirect(url_for('budgets.budgets'))
    
    # Get all budgets for the user
    budgets = Budget.query.filter_by(user_id=session['user_id']).all()
    
    # Calculate spent amounts for each budget
    for budget in budgets:
        try:
            spent = db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
                Expense.user_id == session['user_id'],
                Expense.category == budget.category
            ).scalar() or 0
            budget.spent = float(spent)
        except Exception as e:
            print(f"Error calculating spent amount: {e}")
            budget.spent = 0.0
    
    return render_template('budgets.html', budgets=budgets)
