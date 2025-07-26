from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from app.models import Income
from app import db
from datetime import datetime

income_bp = Blueprint('income', __name__)

@income_bp.route('/income', methods=['GET', 'POST'])
def income():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        try:
            income = Income(
                user_id=session['user_id'],
                source=request.form['source'],
                amount=float(request.form['amount']),
                description=request.form.get('description', ''),
                date=datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            )
            db.session.add(income)
            db.session.commit()
            flash('Income added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            print(f"Income creation error: {e}")
            flash('Error adding income. Please try again.', 'error')
        
        return redirect(url_for('income.income'))
    
    incomes = Income.query.filter_by(user_id=session['user_id']).order_by(Income.date.desc()).all()
    return render_template('income.html', incomes=incomes)

@income_bp.route('/edit_income/<int:income_id>', methods=['GET', 'POST'])
def edit_income(income_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    income = Income.query.filter_by(id=income_id, user_id=session['user_id']).first()
    if not income:
        flash('Income not found!', 'error')
        return redirect(url_for('income.income'))
    
    if request.method == 'POST':
        try:
            income.source = request.form['source']
            income.amount = float(request.form['amount'])
            income.description = request.form.get('description', '')
            income.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            
            db.session.commit()
            flash('Income updated successfully!', 'success')
            return redirect(url_for('income.income'))
        except Exception as e:
            db.session.rollback()
            print(f"Income update error: {e}")
            flash('Error updating income. Please try again.', 'error')
    
    return render_template('edit_income.html', income=income)

@income_bp.route('/delete_income/<int:income_id>', methods=['POST'])
def delete_income(income_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        income = Income.query.filter_by(id=income_id, user_id=session['user_id']).first()
        if income:
            db.session.delete(income)
            db.session.commit()
            flash('Income deleted successfully!', 'success')
        else:
            flash('Income not found!', 'error')
    except Exception as e:
        db.session.rollback()
        print(f"Income deletion error: {e}")
        flash('Error deleting income. Please try again.', 'error')
    
    return redirect(url_for('income.income'))

@income_bp.route('/get_income/<int:income_id>')
def get_income(income_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    income = Income.query.filter_by(id=income_id, user_id=session['user_id']).first()
    if income:
        return jsonify({
            'id': income.id,
            'source': income.source,
            'amount': income.amount,
            'description': income.description,
            'date': income.date.strftime('%Y-%m-%d')
        })
    else:
        return jsonify({'error': 'Income not found'}), 404
