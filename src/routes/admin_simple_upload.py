from flask import Blueprint, request, redirect, url_for, flash

# Create a completely separate test route to avoid admin conflicts
test_bp = Blueprint('test', __name__, url_prefix='/test')

@test_bp.route('/upload', methods=['GET', 'POST'])
def test_upload():
    """Completely separate upload test"""
    if request.method == 'POST':
        flash('🚨 TEST UPLOAD POST RECEIVED!', 'success')
        flash(f'Form data: {dict(request.form)}', 'info')
        flash(f'Files: {list(request.files.keys())}', 'info')
        return redirect(request.url)
    
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Upload - SEPARATE ROUTE</title>
        <style>
            body { background: #2c3e50; color: white; font-family: Arial; padding: 20px; }
            form { max-width: 400px; margin: 0 auto; }
            input, button { display: block; width: 100%; margin: 10px 0; padding: 10px; }
            button { background: #f57931; color: white; border: none; cursor: pointer; }
            .version { color: #f57931; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>Test Upload - SEPARATE ROUTE</h1>
        <p class="version">URL: /test/upload - NO ADMIN CONFLICTS</p>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="test_file">
            <input type="text" name="test_text" placeholder="Test text">
            <button type="submit">Test Upload</button>
        </form>
        <p><a href="/admin/dashboard" style="color: #f57931;">Back to Dashboard</a></p>
    </body>
    </html>
    """

