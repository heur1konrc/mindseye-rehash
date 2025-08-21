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
    images = []
    try:
        with open('static/portfolio.json', 'r') as f:
            portfolio_data = json.load(f)
        images = portfolio_data.get('images', [])
    except:
        images = []
    
    # Build image HTML
    image_html = ""
    for img in images:
        category = img.get('categories', [{}])[0].get('name', 'None') if img.get('categories') else 'None'
        image_html += f'''
        <div class="image-item">
            <img src="/static/{img.get('filename', '')}" alt="{img.get('title', '')}">
            <div class="image-info">
                <h3>{img.get('title', '')}</h3>
                <p>{img.get('description', '')}</p>
                <p>Category: {category}</p>
                <p>Camera: {img.get('camera_make', '')}</p>
                <p>Lens: {img.get('lens', '')}</p>
            </div>
        </div>
        '''
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mind's Eye Photography - Admin Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; margin: 0; padding: 2rem; }
            .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
            h1 { color: #ff6b35; }
            .logout { background: #666; color: white; padding: 0.5rem 1rem; text-decoration: none; border-radius: 4px; }
            .upload-section { background: #2a2a2a; padding: 2rem; border-radius: 8px; margin-bottom: 2rem; }
            .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }
            .image-item { background: #2a2a2a; border-radius: 8px; overflow: hidden; }
            .image-item img { width: 100%; height: 150px; object-fit: cover; }
            .image-info { padding: 1rem; }
            .image-info h3 { margin: 0 0 0.5rem 0; color: #ff6b35; }
            .image-info p { margin: 0.25rem 0; font-size: 0.9rem; color: #ccc; }
            input, textarea, select { width: 100%; padding: 0.8rem; margin: 0.5rem 0; border: 1px solid #444; background: #333; color: #fff; border-radius: 4px; }
            button { padding: 0.8rem 1.5rem; background: #ff6b35; color: white; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #e55a2b; }
            .success { background: #4CAF50; color: white; padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }
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
        
        <h2>Current Portfolio (''' + str(len(images)) + ''' images)</h2>
        <div class="gallery">
        ''' + image_html + '''
        </div>
        
        <div style="margin-top: 2rem; padding: 1rem; background: #2a2a2a; border-radius: 8px;">
            <h3>Admin Features Available:</h3>
            <p>✅ Image Upload & Management</p>
            <p>✅ Portfolio Display</p>
            <p>✅ Category Assignment</p>
            <p>🔧 Enhanced features will be added gradually</p>
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
    
    # Check if the post request has the file part
    if 'image' not in request.files:
        flash('No file part')
        return redirect(url_for('admin.admin_dashboard'))
    
    file = request.files['image']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('admin.admin_dashboard'))
    
    if file:
        # Generate a unique filename
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        file_path = os.path.join('static', filename)
        file.save(file_path)
        
        # Get form data
        title = request.form.get('title', 'Untitled')
        description = request.form.get('description', '')
        category = request.form.get('category', 'Nature')
        
        # Load existing portfolio data
        try:
            with open('static/portfolio.json', 'r') as f:
                portfolio_data = json.load(f)
        except:
            portfolio_data = {'images': []}
        
        # Add new image
        new_image = {
            'id': len(portfolio_data['images']) + 1,
            'title': title,
            'description': description,
            'filename': filename,
            'categories': [{'name': category}],
            'camera_make': 'Canon EOS R8',
            'lens': 'EF24-105mm f/4L IS USM',
            'created_at': datetime.now().isoformat(),
            'is_active': True
        }
        
        portfolio_data['images'].append(new_image)
        
        # Save updated portfolio data
        with open('static/portfolio.json', 'w') as f:
            json.dump(portfolio_data, f, indent=2)
        
        return redirect(url_for('admin.admin_dashboard'))

