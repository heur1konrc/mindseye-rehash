from flask import Blueprint, request, redirect, url_for, flash

# Create a simple test upload route
admin_simple_bp = Blueprint('admin_simple', __name__, url_prefix='/admin')

@admin_simple_bp.route('/simple-upload', methods=['GET', 'POST'])
def simple_upload():
    """Simple upload test"""
    if request.method == 'POST':
        flash('🚨 SIMPLE UPLOAD POST RECEIVED!', 'success')
        flash(f'Form data: {dict(request.form)}', 'info')
        flash(f'Files: {list(request.files.keys())}', 'info')
        return redirect(request.url)
    
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simple Upload Test - REBUILD v2</title>
        <style>
            body { background: #2c3e50; color: white; font-family: Arial; padding: 20px; }
            form { max-width: 400px; margin: 0 auto; }
            input, button { display: block; width: 100%; margin: 10px 0; padding: 10px; }
            button { background: #f57931; color: white; border: none; cursor: pointer; }
            .version { color: #f57931; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>Simple Upload Test</h1>
        <p class="version">VERSION: REBUILD v2 - NO REQUIRED ATTRIBUTE</p>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="test_file">
            <input type="text" name="test_text" placeholder="Test text">
            <button type="submit">Test Upload</button>
        </form>
        <p><a href="/admin/dashboard" style="color: #f57931;">Back to Dashboard</a></p>
    </body>
    </html>
    """

