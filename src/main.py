from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'mindseye2025'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Import all admin routes
from routes.admin import admin_bp
from routes.background import background_bp
from routes.backup import backup_bp
from routes.category_management import category_mgmt_bp
from routes.contact import contact_bp
from routes.featured_image import featured_bp
from routes.portfolio_management import portfolio_mgmt_bp

# Register all blueprints
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(background_bp, url_prefix='/admin/background')
app.register_blueprint(backup_bp, url_prefix='/admin/backup')
app.register_blueprint(category_mgmt_bp, url_prefix='/admin/categories')
app.register_blueprint(contact_bp, url_prefix='/admin/contact')
app.register_blueprint(featured_bp, url_prefix='/admin/featured')
app.register_blueprint(portfolio_mgmt_bp, url_prefix='/admin/portfolio')

@app.route('/')
def index():
    """Serve the React frontend"""
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

