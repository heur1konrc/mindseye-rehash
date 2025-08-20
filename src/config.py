import os

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
DATABASE_DIR = os.path.join(BASE_DIR, 'database')

# Photography assets
PHOTOGRAPHY_ASSETS_DIR = STATIC_DIR
UPLOAD_FOLDER = STATIC_DIR

# Data files
PORTFOLIO_DATA_FILE = os.path.join(STATIC_DIR, 'portfolio.json')
CATEGORIES_CONFIG_FILE = os.path.join(STATIC_DIR, 'categories.json')
BACKGROUND_CONFIG_FILE = os.path.join(STATIC_DIR, 'background.json')
FEATURED_CONFIG_FILE = os.path.join(STATIC_DIR, 'featured.json')

# Upload settings
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_image_url(filename):
    """Get URL for image file"""
    return f'/static/{filename}'

# Ensure directories exist
os.makedirs(PHOTOGRAPHY_ASSETS_DIR, exist_ok=True)
os.makedirs(DATABASE_DIR, exist_ok=True)


# Legacy assets directory (for backward compatibility)
LEGACY_ASSETS_DIR = STATIC_DIR

# Additional config files
BACKGROUND_CONFIG_FILE = os.path.join(STATIC_DIR, 'background-config.json')
CONTACT_CONFIG_FILE = os.path.join(STATIC_DIR, 'contact-config.json')

# Database file
DATABASE_FILE = os.path.join(DATABASE_DIR, 'app.db')

# Admin settings
ADMIN_PASSWORD = "mindseye2025"

