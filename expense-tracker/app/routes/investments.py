from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.models import Investment
from app import db
from datetime import datetime

investments_bp = Blueprint('investments', __name__)

@investments_bp.route('/investments', methods=['GET', 'POST'])
def investments():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        investment = Investment(
            user_id=session['user_id'],
            investment_type=request.form['investment_type'],
            amount=float(request.form['amount']),
            description=request.form.get('description', ''),
            date=datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        )
        db.session.add(investment)
        db.session.commit()
        flash('Investment added successfully!', 'success')
        return redirect(url_for('investments.investments'))
    
    investments = Investment.query.filter_by(user_id=session['user_id']).order_by(Investment.date.desc()).all()
    return render_template('investments.html', investments=investments)
