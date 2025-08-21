"""
Frontend routes for the website
"""
from flask import Blueprint, render_template, send_from_directory, current_app
import os

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
def home():
    """Home page"""
    return render_template('frontend/home.html')

@frontend_bp.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory(os.path.join(current_app.root_path, 'static'), filename)

