"""
Frontend routes for the website
"""
from flask import Blueprint, render_template, send_from_directory, current_app, request, redirect, url_for, jsonify
import os
import sys
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Add the parent directory to the path so we can import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from models import db, Image, Category, ImageCategory, FeaturedImage, BackgroundSetting, ContactMessage

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
def home():
    """Home page"""
    try:
        return render_template('frontend/home.html')
    except Exception as e:
        logger.error(f"Error rendering home page: {str(e)}")
        return render_template('error.html', error_code=500, error_message=f"Error rendering home page: {str(e)}"), 500

@frontend_bp.route('/portfolio')
def portfolio():
    """Portfolio page"""
    try:
        return render_template('frontend/portfolio.html')
    except Exception as e:
        logger.error(f"Error rendering portfolio page: {str(e)}")
        return render_template('error.html', error_code=500, error_message=f"Error rendering portfolio page: {str(e)}"), 500

@frontend_bp.route('/featured')
def featured():
    """Featured image page"""
    try:
        return render_template('frontend/featured.html')
    except Exception as e:
        logger.error(f"Error rendering featured page: {str(e)}")
        return render_template('error.html', error_code=500, error_message=f"Error rendering featured page: {str(e)}"), 500

@frontend_bp.route('/about')
def about():
    """About page"""
    try:
        return render_template('frontend/about.html')
    except Exception as e:
        logger.error(f"Error rendering about page: {str(e)}")
        return render_template('error.html', error_code=500, error_message=f"Error rendering about page: {str(e)}"), 500

@frontend_bp.route('/contact')
def contact():
    """Contact page"""
    try:
        return render_template('frontend/contact.html')
    except Exception as e:
        logger.error(f"Error rendering contact page: {str(e)}")
        return render_template('error.html', error_code=500, error_message=f"Error rendering contact page: {str(e)}"), 500

@frontend_bp.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory(os.path.join(current_app.root_path, 'static'), filename)

