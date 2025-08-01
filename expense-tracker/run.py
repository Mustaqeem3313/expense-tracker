import os
from app import create_app, db

app = create_app()

if __name__ == '__main__':
    # For production deployment
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
