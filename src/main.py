from flask import Flask, render_template, send_from_directory, request, redirect, url_for, jsonify
import os
import sys
import logging
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# FORCE RAILWAY REBUILD - DEPLOYMENT ISSUE DETECTED - USERS NOT GETTING UPDATES

# Add the current directory to the path so we can import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Now we can import our modules
from models import db, init_db, import_legacy_data, Image

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
from routes.admin_simple_upload import test_bp
from routes.frontend import frontend_bp
from routes.api import api_bp

# Register blueprints
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(test_bp)
app.register_blueprint(frontend_bp)
app.register_blueprint(api_bp, url_prefix='/api')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error_code=500, error_message="Server error"), 500

# Direct Flask POST test (not in blueprint)
@app.route('/direct-test', methods=['GET', 'POST'])
def direct_test():
    if request.method == 'POST':
        return """
        <h1 style="color: green;">🎉 DIRECT FLASK POST WORKS! 🎉</h1>
        <p>Form data: {}</p>
        <p><a href="/direct-test">Test Again</a></p>
        """.format(dict(request.form))
    
    return """
    <html>
    <body style="background: #2c3e50; color: white; font-family: Arial; padding: 20px;">
        <h1>Direct Flask POST Test</h1>
        <p>This route is directly on the Flask app, not in a blueprint</p>
        <form method="POST">
            <input type="text" name="test_input" placeholder="Enter test text" style="padding: 10px; margin: 10px 0; display: block;">
            <button type="submit" style="padding: 10px 20px; background: #f57931; color: white; border: none;">Test Direct POST</button>
        </form>
        <p><a href="/admin/dashboard" style="color: #f57931;">Back to Dashboard</a></p>
    </body>
    </html>
    """

# Working admin upload route (direct Flask, not blueprint)
@app.route('/admin-upload', methods=['GET', 'POST'])
def admin_upload():
    if request.method == 'POST':
        try:
            # Get form data
            title_prefix = request.form.get('title_prefix', 'Image')
            description = request.form.get('description', '')
            
            # Get uploaded files
            files = request.files.getlist('images[]')
            if not files or files[0].filename == '':
                return """
                <h1 style="color: red;">❌ No files selected</h1>
                <p><a href="/admin-upload">Try Again</a></p>
                """
            
            uploaded_count = 0
            for i, file in enumerate(files):
                if file and file.filename:
                    try:
                        # Generate unique filename
                        filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
                        
                        # Save file to correct path: src/static/assets
                        upload_path = os.path.join('src', 'static', 'assets', filename)
                        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                        file.save(upload_path)
                        
                        # Create database record
                        image = Image(
                            title=f"{title_prefix} {i+1}",
                            filename=filename,
                            description=description,
                            date_uploaded=datetime.now()
                        )
                        db.session.add(image)
                        uploaded_count += 1
                        
                    except Exception as file_error:
                        return f"""
                        <h1 style="color: red;">❌ File Processing Error</h1>
                        <p>Error processing file {file.filename}: {str(file_error)}</p>
                        <p><a href="/admin-upload">Try Again</a></p>
                        """
            
            # Commit all database changes
            try:
                db.session.commit()
                return f"""
                <h1 style="color: green;">🎉 SUCCESS! Uploaded {uploaded_count} images! 🎉</h1>
                <p>Images saved to database and files stored successfully.</p>
                <p><a href="/admin-upload">Upload More</a></p>
                <p><a href="/admin/dashboard">Back to Dashboard</a></p>
                """
            except Exception as db_error:
                db.session.rollback()
                return f"""
                <h1 style="color: red;">❌ Database Error</h1>
                <p>Files uploaded but database save failed: {str(db_error)}</p>
                <p><a href="/admin-upload">Try Again</a></p>
                """
            
        except Exception as e:
            return f"""
            <h1 style="color: red;">❌ Upload Error</h1>
            <p>Error: {str(e)}</p>
            <p><a href="/admin-upload">Try Again</a></p>
            """
    
    return """
    <html>
    <head>
        <title>Admin Upload - WORKING VERSION</title>
        <style>
            body { background: #2c3e50; color: white; font-family: Arial; padding: 20px; }
            form { max-width: 500px; margin: 0 auto; }
            input, textarea, button { display: block; width: 100%; margin: 10px 0; padding: 10px; box-sizing: border-box; }
            button { background: #f57931; color: white; border: none; cursor: pointer; font-size: 16px; }
            .success { color: #f57931; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>📸 Admin Upload - WORKING VERSION</h1>
        <p class="success">This upload route works because it's direct Flask, not blueprint!</p>
        <form method="POST" enctype="multipart/form-data">
            <label>Select Images:</label>
            <input type="file" name="images[]" multiple accept="image/*" required>
            
            <label>Title Prefix:</label>
            <input type="text" name="title_prefix" placeholder="e.g., Sunset, Wildlife" value="Photo">
            
            <label>Description:</label>
            <textarea name="description" rows="3" placeholder="Describe the images"></textarea>
            
            <button type="submit">📤 Upload Images</button>
        </form>
        <p><a href="/admin/dashboard" style="color: #f57931;">← Back to Dashboard</a></p>
    </body>
    </html>
    """

@app.route('/admin-gallery')
def admin_gallery():
    """Visual gallery management - see all images with thumbnails"""
    try:
        # Get all images from database
        images = Image.query.order_by(Image.date_uploaded.desc()).all()
        
        # Build image grid HTML
        image_grid = ""
        for image in images:
            image_url = f"/static/assets/{image.filename}"
            image_grid += f"""
            <div class="image-card" data-image-id="{image.id}">
                <img src="{image_url}" alt="{image.title}" class="thumbnail">
                <div class="image-info">
                    <h4>{image.title}</h4>
                    <p class="filename">{image.filename}</p>
                    <p class="description">{image.description or 'No description'}</p>
                    <p class="upload-date">Uploaded: {image.date_uploaded.strftime('%Y-%m-%d %H:%M')}</p>
                    <div class="image-actions">
                        <button onclick="editImage({image.id})" class="edit-btn">✏️ Edit</button>
                        <button onclick="deleteImage({image.id})" class="delete-btn">🗑️ Delete</button>
                        <button onclick="categorizeImage({image.id})" class="category-btn">📁 Categorize</button>
                    </div>
                </div>
            </div>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>📸 Visual Gallery Management</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #2c3e50; color: white; margin: 0; padding: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .header h1 {{ color: #f57931; margin: 0; }}
                .stats {{ background: #34495e; padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: center; }}
                .image-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
                .image-card {{ background: #34495e; border-radius: 8px; padding: 15px; border: 2px solid transparent; transition: all 0.3s; }}
                .image-card:hover {{ border-color: #f57931; transform: translateY(-2px); }}
                .thumbnail {{ width: 100%; height: 200px; object-fit: cover; border-radius: 5px; margin-bottom: 10px; }}
                .image-info h4 {{ color: #f57931; margin: 0 0 5px 0; }}
                .filename {{ font-size: 12px; color: #bdc3c7; margin: 5px 0; word-break: break-all; }}
                .description {{ margin: 10px 0; }}
                .upload-date {{ font-size: 12px; color: #95a5a6; margin: 5px 0; }}
                .image-actions {{ margin-top: 15px; }}
                .image-actions button {{ padding: 8px 12px; margin: 2px; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; }}
                .edit-btn {{ background: #3498db; color: white; }}
                .delete-btn {{ background: #e74c3c; color: white; }}
                .category-btn {{ background: #f57931; color: white; }}
                .nav-links {{ text-align: center; margin: 20px 0; }}
                .nav-links a {{ color: #f57931; text-decoration: none; margin: 0 15px; }}
                .nav-links a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📸 Visual Gallery Management</h1>
                <p>See and manage all your uploaded images</p>
            </div>
            
            <div class="stats">
                <strong>Total Images: {len(images)}</strong>
            </div>
            
            <div class="nav-links">
                <a href="/admin-upload">📤 Upload More Images</a>
                <a href="/admin/dashboard">📊 Back to Dashboard</a>
                <a href="/admin-categories">📁 Manage Categories</a>
            </div>
            
            <div class="image-grid">
                {image_grid if images else '<p style="text-align: center; grid-column: 1/-1;">No images uploaded yet. <a href="/admin-upload">Upload some images!</a></p>'}
            </div>
            
            <script>
                function editImage(imageId) {{
                    alert('Edit functionality coming soon! Image ID: ' + imageId);
                }}
                
                function deleteImage(imageId) {{
                    if (confirm('Are you sure you want to delete this image?')) {{
                        alert('Delete functionality coming soon! Image ID: ' + imageId);
                    }}
                }}
                
                function categorizeImage(imageId) {{
                    alert('Categorize functionality coming soon! Image ID: ' + imageId);
                }}
            </script>
        </body>
        </html>
        """
        
    except Exception as e:
        return f"""
        <h1 style="color: red;">❌ Gallery Error</h1>
        <p>Error loading gallery: {str(e)}</p>
        <p><a href="/admin-upload">Back to Upload</a></p>
        """

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

