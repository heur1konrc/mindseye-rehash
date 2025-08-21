from flask import Flask, render_template, send_from_directory, request, redirect, url_for, jsonify
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# FORCE RAILWAY REBUILD - DEPLOYMENT ISSUE DETECTED - USERS NOT GETTING UPDATES

# Add the current directory to the path so we can import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Now we can import our modules
from models import db, init_db, import_legacy_data

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'mindseye2025'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Use persistent volume for database in production
if os.environ.get('RAILWAY_ENVIRONMENT') == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////mnt/data/mindseye.db'
    logger.info("Using persistent volume database at /mnt/data/mindseye.db")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/ubuntu/mindseye-rehash/src/database/mindseye.db'
    logger.info(f"Using local database at {app.config['SQLALCHEMY_DATABASE_URI']}")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure database directory exists
if os.environ.get('RAILWAY_ENVIRONMENT') == 'production':
    os.makedirs('/mnt/data', exist_ok=True)
    logger.info("Ensured /mnt/data directory exists for persistent volume")
else:
    os.makedirs(os.path.join(os.path.dirname(__file__), 'database'), exist_ok=True)
    logger.info("Ensured local database directory exists")

# Initialize database
init_db(app)
logger.info("Database initialized")

# Import legacy data if available
try:
    import_legacy_data('static/portfolio.json')
    logger.info("Legacy data imported successfully")
except Exception as e:
    logger.error(f"Error importing legacy data: {e}")

# Import routes
from routes.admin import admin_bp
from routes.admin_simple_upload import admin_simple_bp
from routes.frontend import frontend_bp
from routes.api import api_bp

# Register blueprints
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(admin_simple_bp)
app.register_blueprint(frontend_bp)
app.register_blueprint(api_bp, url_prefix='/api')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_code=500, error_message="Server error"), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

