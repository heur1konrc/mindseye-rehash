from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'mindseye2025'

# Import admin routes
from routes.admin import admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')

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

