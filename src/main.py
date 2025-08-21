from flask import Flask, render_template, send_from_directory, request, redirect, url_for, jsonify
import os
import sys

# Add the current directory to the path so we can import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Now we can import our modules
from models import db, init_db, import_legacy_data

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'mindseye2025'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Use relative path for database in production
if os.environ.get('RAILWAY_ENVIRONMENT') == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/mindseye.db'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/ubuntu/mindseye-rehash/src/database/mindseye.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure database directory exists
os.makedirs(os.path.join(os.path.dirname(__file__), 'database'), exist_ok=True)

# Initialize database
init_db(app)

# Import legacy data if available
import_legacy_data('static/portfolio.json')

# Import routes
from routes.admin import admin_bp
from routes.frontend import frontend_bp

# Register blueprints
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(frontend_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

