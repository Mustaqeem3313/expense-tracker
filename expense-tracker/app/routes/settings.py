from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.models import User, UserSettings
from app import db

settings_bp = Blueprint('settings', __name__)

def get_currency_symbol(currency):
    """Get currency symbol for display"""
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'INR': '₹'
    }
    return symbols.get(currency, '$')

@settings_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    
    # Get or create user settings
    user_settings = UserSettings.query.filter_by(user_id=session['user_id']).first()
    if not user_settings:
        user_settings = UserSettings(user_id=session['user_id'])
        db.session.add(user_settings)
        db.session.commit()
    
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        
        try:
            if form_type == 'personal_info':
                user.name = request.form['name']
                user.email = request.form['email']
                # Update session with new name
                session['user_name'] = user.name
                session['user_email'] = user.email
                db.session.commit()
                flash('Personal information updated successfully!', 'success')
            
            elif form_type == 'change_password':
                current_password = request.form.get('current_password')
                new_password = request.form.get('new_password')
                confirm_new_password = request.form.get('confirm_new_password')
                
                if user.check_password(current_password):
                    if new_password == confirm_new_password:
                        if len(new_password) >= 6:
                            user.set_password(new_password)
                            db.session.commit()
                            flash('Password changed successfully!', 'success')
                        else:
                            flash('New password must be at least 6 characters long!', 'error')
                    else:
                        flash('New passwords do not match!', 'error')
                else:
                    flash('Current password is incorrect!', 'error')
            
            elif form_type == 'app_settings':
                # Update currency and other settings
                old_currency = user_settings.currency
                user_settings.currency = request.form.get('currency', 'USD')
                user_settings.notifications = request.form.get('notifications', 'enabled')
                
                # Update session with new currency
                session['user_currency'] = user_settings.currency
                session['currency_symbol'] = get_currency_symbol(user_settings.currency)
                
                db.session.commit()
                
                if old_currency != user_settings.currency:
                    flash(f'Currency changed to {user_settings.currency} successfully! Page will refresh to apply changes.', 'success')
                else:
                    flash('Settings saved successfully!', 'success')
        
        except Exception as e:
            db.session.rollback()
            print(f"Settings update error: {e}")
            flash('Error updating settings. Please try again.', 'error')
        
        return redirect(url_for('settings.settings'))
    
    return render_template('settings.html', user=user, user_settings=user_settings)

@settings_bp.route('/export_data')
def export_data():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # This would implement actual data export
    flash('Data export feature coming soon!', 'info')
    return redirect(url_for('settings.settings'))

@settings_bp.route('/reset_data')
def reset_data():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # This would implement data reset
    flash('Data reset feature coming soon! Contact support for assistance.', 'warning')
    return redirect(url_for('settings.settings'))
