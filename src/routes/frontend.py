"""
Frontend routes for the website
"""
from flask import Blueprint, render_template, send_from_directory, current_app, request, redirect, url_for, jsonify
import os
import sys

# Add the parent directory to the path so we can import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from models import db, Image, Category, ImageCategory, FeaturedImage, BackgroundSetting, ContactMessage

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
def index():
    """Home page"""
    return render_template('frontend/home.html')

@frontend_bp.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory(os.path.join(current_app.root_path, 'static'), filename)

