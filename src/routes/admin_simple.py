from flask import Blueprint

# Create a simple admin test blueprint
admin_simple_bp = Blueprint('admin_simple', __name__)

@admin_simple_bp.route('/admin-test')
def admin_test():
    """Simple admin test route"""
    return """
    <html>
    <head><title>Admin Test</title></head>
    <body style="background: #2c3e50; color: white; font-family: Arial; text-align: center; padding: 50px;">
        <h1>🎉 Admin Blueprint Working!</h1>
        <p>This confirms the admin system can work.</p>
        <a href="/" style="color: #f57931;">Back to Home</a>
    </body>
    </html>
    """

