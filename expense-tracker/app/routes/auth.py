from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.models import User, UserSettings
from app import db

auth_bp = Blueprint('auth', __name__)

def get_currency_symbol(currency):
    """Get currency symbol for display"""
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'INR': '₹'
    }
    return symbols.get(currency, '$')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please fill in all fields!', 'error')
            return render_template('login.html')
        
        try:
            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password):
                # Set session variables
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_email'] = user.email
                
                # Get user settings for currency
                user_settings = UserSettings.query.filter_by(user_id=user.id).first()
                if user_settings:
                    session['user_currency'] = user_settings.currency
                    session['currency_symbol'] = get_currency_symbol(user_settings.currency)
                else:
                    session['user_currency'] = 'USD'
                    session['currency_symbol'] = '$'
                
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard.dashboard'))
            else:
                flash('Invalid email or password!', 'error')
                
        except Exception as e:
            print(f"Login error: {e}")
            flash('An error occurred during login. Please try again.', 'error')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([name, email, password, confirm_password]):
            flash('Please fill in all fields!', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')
        
        try:
            # Check if user exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email already registered!', 'error')
                return render_template('register.html')
            
            # Create new user
            user = User(name=name, email=email)
            user.set_password(password)
            
            db.session.add(user)
            db.session.flush()  # Flush to get user.id
            
            # Create default user settings
            user_settings = UserSettings(
                user_id=user.id,
                currency='USD',
                notifications='enabled'
            )
            db.session.add(user_settings)
            
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Registration error: {e}")
            flash('An error occurred during registration. Please try again.', 'error')
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully!', 'info')
    return redirect(url_for('main.index'))
