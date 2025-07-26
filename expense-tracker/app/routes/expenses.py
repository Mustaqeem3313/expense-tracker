from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from app.models import Expense
from app import db
from datetime import datetime

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('/expenses', methods=['GET', 'POST'])
def expenses():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        try:
            # Handle expense creation
            expense = Expense(
                user_id=session['user_id'],
                category=request.form['category'],
                amount=float(request.form['amount']),
                description=request.form.get('description', ''),
                date=datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            )
            db.session.add(expense)
            db.session.commit()
            flash('Expense added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            print(f"Expense creation error: {e}")
            flash('Error adding expense. Please try again.', 'error')
        
        return redirect(url_for('expenses.expenses'))
    
    # Get all expenses for the user
    expenses = Expense.query.filter_by(user_id=session['user_id']).order_by(Expense.date.desc()).all()
    return render_template('expenses.html', expenses=expenses)

@expenses_bp.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    expense = Expense.query.filter_by(id=expense_id, user_id=session['user_id']).first()
    if not expense:
        flash('Expense not found!', 'error')
        return redirect(url_for('expenses.expenses'))
    
    if request.method == 'POST':
        try:
            expense.category = request.form['category']
            expense.amount = float(request.form['amount'])
            expense.description = request.form.get('description', '')
            expense.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            
            db.session.commit()
            flash('Expense updated successfully!', 'success')
            return redirect(url_for('expenses.expenses'))
        except Exception as e:
            db.session.rollback()
            print(f"Expense update error: {e}")
            flash('Error updating expense. Please try again.', 'error')
    
    return render_template('edit_expense.html', expense=expense)

@expenses_bp.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        expense = Expense.query.filter_by(id=expense_id, user_id=session['user_id']).first()
        if expense:
            db.session.delete(expense)
            db.session.commit()
            flash('Expense deleted successfully!', 'success')
        else:
            flash('Expense not found!', 'error')
    except Exception as e:
        db.session.rollback()
        print(f"Expense deletion error: {e}")
        flash('Error deleting expense. Please try again.', 'error')
    
    return redirect(url_for('expenses.expenses'))

@expenses_bp.route('/get_expense/<int:expense_id>')
def get_expense(expense_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    expense = Expense.query.filter_by(id=expense_id, user_id=session['user_id']).first()
    if expense:
        return jsonify({
            'id': expense.id,
            'category': expense.category,
            'amount': expense.amount,
            'description': expense.description,
            'date': expense.date.strftime('%Y-%m-%d')
        })
    else:
        return jsonify({'error': 'Expense not found'}), 404
