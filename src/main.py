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
                    # Generate unique filename
                    filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
                    
                    # Save file
                    upload_path = os.path.join(app.static_folder, 'assets', filename)
                    os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                    file.save(upload_path)
                    
                    # Create database record
                    image = Image(
                        title=f"{title_prefix} {i+1}",
                        filename=filename,
                        description=description,
                        upload_date=datetime.now()
                    )
                    db.session.add(image)
                    uploaded_count += 1
            
            db.session.commit()
            
            return f"""
            <h1 style="color: green;">🎉 SUCCESS! Uploaded {uploaded_count} images! 🎉</h1>
            <p><a href="/admin-upload">Upload More</a></p>
            <p><a href="/admin/dashboard">Back to Dashboard</a></p>
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

