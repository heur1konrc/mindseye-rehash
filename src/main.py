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
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from models import db, init_db, import_legacy_data, Image

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'mindseye2025'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max total upload size

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
                        
                        # Save file to Railway volume in production, local path in development
                        if os.path.exists('/mnt/data'):
                            # Production: Use Railway volume
                            upload_path = os.path.join('/mnt/data', filename)
                        else:
                            # Development: Use local path
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
            # Use the new uploads route for serving files
            image_url = f"/uploads/{image.filename}"
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
                        // Create form and submit to delete route
                        const form = document.createElement('form');
                        form.method = 'POST';
                        form.action = '/admin/delete-image/' + imageId;
                        document.body.appendChild(form);
                        form.submit();
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

@app.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    """Serve uploaded files from volume or static assets"""
    # First try volume (for new uploads)
    if os.path.exists('/mnt/data') and os.path.exists(f'/mnt/data/{filename}'):
        return send_from_directory('/mnt/data', filename)
    # Fall back to static assets (for original images)
    elif os.path.exists(f'src/static/assets/{filename}'):
        return send_from_directory('src/static/assets', filename)
    # Development fallback
    else:
        return send_from_directory('static/assets', filename)

@app.route('/admin/emergency-delete-sunset')
def emergency_delete_sunset():
    """Emergency route to delete the stubborn sunset image"""
    try:
        from models import Image, FeaturedImage
        
        # Find sunset image
        sunset = Image.query.filter(Image.title.like('%Sunset%')).first()
        if sunset:
            filename = sunset.filename
            title = sunset.title
            
            # First, remove any featured image references
            featured_refs = FeaturedImage.query.filter_by(image_id=sunset.id).all()
            for ref in featured_refs:
                db.session.delete(ref)
            
            # Then delete the main image
            db.session.delete(sunset)
            db.session.commit()
            
            return f"""
            <h1 style="color: green;">✅ Sunset Image Deleted!</h1>
            <p>Deleted: {title} ({filename})</p>
            <p>Removed {len(featured_refs)} featured image references</p>
            <p><a href="/admin-gallery">← Back to Gallery</a></p>
            """
        else:
            return f"""
            <h1 style="color: orange;">⚠️ Sunset Image Not Found</h1>
            <p>The sunset image is already deleted from the database.</p>
            <p><a href="/admin-gallery">← Back to Gallery</a></p>
            """
            
    except Exception as e:
        return f"""
        <h1 style="color: red;">❌ Delete Error</h1>
        <p>Error: {str(e)}</p>
        <p><a href="/admin-gallery">← Back to Gallery</a></p>
        """

@app.route('/admin-categories')
def admin_categories():
    """Category management - view, add, edit, delete categories"""
    try:
        # Import Category model
        from models import Category
        
        # Get all categories
        categories = Category.query.order_by(Category.display_order, Category.name).all()
        
        # Build category management HTML
        category_list = ""
        for category in categories:
            image_count = len(category.images)
            category_list += f"""
            <div class="category-item" style="border: 1px solid #444; margin: 10px 0; padding: 15px; border-radius: 8px; background: #2a2a2a;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="color: {category.color_code}; margin: 0;">{category.name}</h4>
                        <p style="color: #ccc; margin: 5px 0;">{category.description or 'No description'}</p>
                        <p style="color: #888; font-size: 14px;">{image_count} images • Order: {category.display_order}</p>
                    </div>
                    <div>
                        <button onclick="editCategory({category.id})" style="background: #4CAF50; color: white; border: none; padding: 8px 12px; margin: 2px; border-radius: 4px; cursor: pointer;">✏️ Edit</button>
                        <button onclick="deleteCategory({category.id})" style="background: #f44336; color: white; border: none; padding: 8px 12px; margin: 2px; border-radius: 4px; cursor: pointer;">🗑️ Delete</button>
                    </div>
                </div>
            </div>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Category Management - Mind's Eye Photography</title>
            <style>
                body {{ background: #1a1a1a; color: #fff; font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .add-category {{ background: #f57931; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 16px; margin-bottom: 20px; }}
                .add-category:hover {{ background: #e66a28; }}
                .category-form {{ background: #2a2a2a; padding: 20px; border-radius: 8px; margin-bottom: 20px; display: none; }}
                .form-group {{ margin-bottom: 15px; }}
                .form-group label {{ display: block; margin-bottom: 5px; color: #f57931; }}
                .form-group input, .form-group textarea {{ width: 100%; padding: 8px; border: 1px solid #444; background: #333; color: #fff; border-radius: 4px; }}
                .form-buttons {{ text-align: right; }}
                .form-buttons button {{ padding: 8px 16px; margin-left: 10px; border: none; border-radius: 4px; cursor: pointer; }}
                .save-btn {{ background: #4CAF50; color: white; }}
                .cancel-btn {{ background: #666; color: white; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🗂️ Category Management</h1>
                <p>Manage your photography categories</p>
                <p><strong>Total Categories: {len(categories)}</strong></p>
                
                <a href="/admin-gallery" style="color: #f57931; text-decoration: none; margin: 0 15px;">📸 Gallery</a>
                <a href="/admin-upload" style="color: #f57931; text-decoration: none; margin: 0 15px;">📤 Upload</a>
                <a href="/admin/dashboard" style="color: #f57931; text-decoration: none; margin: 0 15px;">📊 Dashboard</a>
            </div>
            
            <button class="add-category" onclick="showAddForm()">➕ Add New Category</button>
            
            <div id="addForm" class="category-form">
                <h3>Add New Category</h3>
                <form method="POST" action="/admin/add-category">
                    <div class="form-group">
                        <label>Category Name:</label>
                        <input type="text" name="name" required placeholder="e.g., Landscapes, Portraits">
                    </div>
                    <div class="form-group">
                        <label>Description:</label>
                        <textarea name="description" placeholder="Optional description"></textarea>
                    </div>
                    <div class="form-group">
                        <label>Color Code:</label>
                        <input type="color" name="color_code" value="#f57931">
                    </div>
                    <div class="form-group">
                        <label>Display Order:</label>
                        <input type="number" name="display_order" value="0" min="0">
                    </div>
                    <div class="form-buttons">
                        <button type="button" class="cancel-btn" onclick="hideAddForm()">Cancel</button>
                        <button type="submit" class="save-btn">💾 Save Category</button>
                    </div>
                </form>
            </div>
            
            <div class="categories-list">
                {category_list}
            </div>
            
            <script>
                function showAddForm() {{
                    document.getElementById('addForm').style.display = 'block';
                }}
                
                function hideAddForm() {{
                    document.getElementById('addForm').style.display = 'none';
                }}
                
                function editCategory(categoryId) {{
                    alert('Edit functionality coming soon! Category ID: ' + categoryId);
                }}
                
                function deleteCategory(categoryId) {{
                    if (confirm('Are you sure you want to delete this category?')) {{
                        // Create form and submit
                        const form = document.createElement('form');
                        form.method = 'POST';
                        form.action = '/admin/delete-category/' + categoryId;
                        document.body.appendChild(form);
                        form.submit();
                    }}
                }}
            </script>
        </body>
        </html>
        """
        
    except Exception as e:
        return f"""
        <h1 style="color: red;">❌ Category Management Error</h1>
        <p>Error loading categories: {str(e)}</p>
        <p><a href="/admin-gallery">Back to Gallery</a></p>
        """

@app.route('/admin/add-category', methods=['POST'])
def add_category():
    """Add a new category"""
    try:
        from models import Category
        
        name = request.form.get('name')
        description = request.form.get('description')
        color_code = request.form.get('color_code', '#f57931')
        display_order = int(request.form.get('display_order', 0))
        
        # Create slug from name
        slug = name.lower().replace(' ', '-').replace('&', 'and')
        
        # Create new category
        category = Category(
            name=name,
            slug=slug,
            description=description,
            color_code=color_code,
            display_order=display_order
        )
        
        db.session.add(category)
        db.session.commit()
        
        return f"""
        <h1 style="color: green;">✅ Category Added Successfully!</h1>
        <p>Added: {name}</p>
        <p><a href="/admin-categories">← Back to Categories</a></p>
        """
        
    except Exception as e:
        return f"""
        <h1 style="color: red;">❌ Add Category Error</h1>
        <p>Error adding category: {str(e)}</p>
        <p><a href="/admin-categories">← Back to Categories</a></p>
        """

@app.route('/admin/delete-category/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    """Delete a category"""
    try:
        from models import Category
        
        # Get the category
        category = Category.query.get_or_404(category_id)
        category_name = category.name
        
        # Delete the category
        db.session.delete(category)
        db.session.commit()
        
        return f"""
        <h1 style="color: green;">✅ Category Deleted Successfully!</h1>
        <p>Deleted: {category_name}</p>
        <p><a href="/admin-categories">← Back to Categories</a></p>
        """
        
    except Exception as e:
        return f"""
        <h1 style="color: red;">❌ Delete Category Error</h1>
        <p>Error deleting category: {str(e)}</p>
        <p><a href="/admin-categories">← Back to Categories</a></p>
        """

@app.route('/admin/delete-image/<int:image_id>', methods=['POST'])
def delete_image(image_id):
    """Delete an image from database and file system"""
    try:
        # Get the image record
        image = Image.query.get_or_404(image_id)
        filename = image.filename
        
        # Delete from database
        db.session.delete(image)
        db.session.commit()
        
        # Delete file from volume if it exists
        if os.path.exists('/mnt/data') and os.path.exists(f'/mnt/data/{filename}'):
            os.remove(f'/mnt/data/{filename}')
        # Delete from static assets if it exists
        elif os.path.exists(f'src/static/assets/{filename}'):
            os.remove(f'src/static/assets/{filename}')
        
        return f"""
        <h1 style="color: green;">✅ Image Deleted Successfully!</h1>
        <p>Deleted: {filename}</p>
        <p><a href="/admin-gallery">← Back to Gallery</a></p>
        """
        
    except Exception as e:
        return f"""
        <h1 style="color: red;">❌ Delete Error</h1>
        <p>Error deleting image: {str(e)}</p>
        <p><a href="/admin-gallery">← Back to Gallery</a></p>
        """

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

