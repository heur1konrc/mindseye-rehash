from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash, send_from_directory
import os
import json
import sqlite3
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# Admin password
ADMIN_PASSWORD = 'mindseye2025'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('database/app.db')
    conn.row_factory = sqlite3.Row
    return conn

@admin_bp.route('/')
def admin_login():
    """Admin login page"""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_dashboard'))
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mind's Eye Photography - Admin Login</title>
        <style>
            body { font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .login-form { background: #2a2a2a; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
            input { width: 100%; padding: 0.8rem; margin: 0.5rem 0; border: 1px solid #444; background: #333; color: #fff; border-radius: 4px; }
            button { width: 100%; padding: 0.8rem; background: #ff6b35; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #e55a2b; }
            h2 { text-align: center; color: #ff6b35; }
        </style>
    </head>
    <body>
        <form class="login-form" method="POST">
            <h2>Admin Login</h2>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
    </body>
    </html>
    '''

@admin_bp.route('/', methods=['POST'])
def admin_login_post():
    """Handle admin login"""
    password = request.form.get('password')
    if password == ADMIN_PASSWORD:
        session['admin_logged_in'] = True
        return redirect(url_for('admin.admin_dashboard'))
    else:
        flash('Invalid password')
        return redirect(url_for('admin.admin_login'))

@admin_bp.route('/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    # Get portfolio data
    try:
        with open('static/portfolio.json', 'r') as f:
            portfolio_data = json.load(f)
        images = portfolio_data.get('images', [])
    except:
        images = []
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mind's Eye Photography - Admin Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; margin: 0; padding: 2rem; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }}
            h1 {{ color: #ff6b35; }}
            .logout {{ background: #666; color: white; padding: 0.5rem 1rem; text-decoration: none; border-radius: 4px; }}
            .upload-section {{ background: #2a2a2a; padding: 2rem; border-radius: 8px; margin-bottom: 2rem; }}
            .gallery {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }}
            .image-item {{ background: #2a2a2a; border-radius: 8px; overflow: hidden; }}
            .image-item img {{ width: 100%; height: 150px; object-fit: cover; }}
            .image-info {{ padding: 1rem; }}
            .image-info h3 {{ margin: 0 0 0.5rem 0; color: #ff6b35; }}
            .image-info p {{ margin: 0.25rem 0; font-size: 0.9rem; color: #ccc; }}
            input, textarea, select {{ width: 100%; padding: 0.8rem; margin: 0.5rem 0; border: 1px solid #444; background: #333; color: #fff; border-radius: 4px; }}
            button {{ padding: 0.8rem 1.5rem; background: #ff6b35; color: white; border: none; border-radius: 4px; cursor: pointer; }}
            button:hover {{ background: #e55a2b; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Mind's Eye Photography - Admin Dashboard</h1>
            <a href="/admin/logout" class="logout">Logout</a>
        </div>
        
        <div class="upload-section">
            <h2>Upload New Image</h2>
            <form method="POST" action="/admin/upload" enctype="multipart/form-data">
                <input type="file" name="image" accept="image/*" required>
                <input type="text" name="title" placeholder="Image Title" required>
                <textarea name="description" placeholder="Image Description" rows="3"></textarea>
                <select name="category">
                    <option value="Nature">Nature</option>
                    <option value="Wildlife">Wildlife</option>
                    <option value="Flora">Flora</option>
                    <option value="Pets">Pets</option>
                    <option value="Landscapes">Landscapes</option>
                </select>
                <button type="submit">Upload Image</button>
            </form>
        </div>
        
        <h2>Current Portfolio ({len(images)} images)</h2>
        <div class="gallery">
            {"".join([f'''
            <div class="image-item">
                <img src="/static/{img['filename']}" alt="{img['title']}">
                <div class="image-info">
                    <h3>{img['title']}</h3>
                    <p>{img['description']}</p>
                    <p>Category: {img['categories'][0]['name'] if img['categories'] else 'None'}</p>
                    <p>Camera: {img['camera_make']}</p>
                    <p>Lens: {img['lens']}</p>
                </div>
            </div>
            ''' for img in images])}
        </div>
    </body>
    </html>
    '''

@admin_bp.route('/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.admin_login'))

@admin_bp.route('/upload', methods=['POST'])
def upload_image():
    """Handle image upload"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    # Handle file upload logic here
    # For now, just redirect back to dashboard
    flash('Image upload functionality will be implemented')
    return redirect(url_for('admin.admin_dashboard'))

