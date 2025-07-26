import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Production-ready configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-this-in-production')
    
    # Database configuration - PostgreSQL for production, SQLite for development
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Fix for newer SQLAlchemy with PostgreSQL URLs
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        print("Using PostgreSQL database for production")
    else:
        # Development database (SQLite)
        instance_path = app.instance_path
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "expense_tracker.db")}'
        print("Using SQLite database for development")
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    # Register all blueprints with error handling
    try:
        from app.routes.main import main_bp
        app.register_blueprint(main_bp)
        print("Main blueprint registered successfully!")
    except ImportError as e:
        print(f"Main blueprint import error: {e}")
    
    try:
        from app.routes.auth import auth_bp
        app.register_blueprint(auth_bp)
        print("Auth blueprint registered successfully!")
    except ImportError as e:
        print(f"Auth blueprint import error: {e}")
    
    try:
        from app.routes.dashboard import dashboard_bp
        app.register_blueprint(dashboard_bp)
        print("Dashboard blueprint registered successfully!")
    except ImportError as e:
        print(f"Dashboard blueprint import error: {e}")
    
    try:
        from app.routes.expenses import expenses_bp
        app.register_blueprint(expenses_bp)
        print("Expenses blueprint registered successfully!")
    except ImportError as e:
        print(f"Expenses blueprint import error: {e}")
    
    try:
        from app.routes.income import income_bp
        app.register_blueprint(income_bp)
        print("Income blueprint registered successfully!")
    except ImportError as e:
        print(f"Income blueprint import error: {e}")
    
    try:
        from app.routes.budgets import budgets_bp
        app.register_blueprint(budgets_bp)
        print("Budgets blueprint registered successfully!")
    except ImportError as e:
        print(f"Budgets blueprint import error: {e}")
    
    try:
        from app.routes.investments import investments_bp
        app.register_blueprint(investments_bp)
        print("Investments blueprint registered successfully!")
    except ImportError as e:
        print(f"Investments blueprint import error: {e}")
    
    try:
        from app.routes.reports import reports_bp
        app.register_blueprint(reports_bp)
        print("Reports blueprint registered successfully!")
    except ImportError as e:
        print(f"Reports blueprint import error: {e}")
    
    try:
        from app.routes.settings import settings_bp
        app.register_blueprint(settings_bp)
        print("Settings blueprint registered successfully!")
    except ImportError as e:
        print(f"Settings blueprint import error: {e}")
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully!")
        except Exception as e:
            print(f"Database error: {e}")
    
    return app
