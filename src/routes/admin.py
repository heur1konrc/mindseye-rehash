from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
import os
import sys
import json
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

# Add the parent directory to the path so we can import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from models import db, Image, Category, ImageCategory, FeaturedImage, BackgroundSetting, ContactMessage, Backup, Setting
from utils import save_uploaded_image, extract_exif_data, format_shutter_speed, generate_slug, create_backup, restore_backup

admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin')

# Admin password (will be moved to database settings)
ADMIN_PASSWORD = 'mindseye2025'

# Helper function to check if admin is logged in
def is_admin_logged_in():
    return session.get('admin_logged_in', False)

# Helper function to check if file extension is allowed
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper function to get database size
def get_db_size():
    try:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'mindseye.db')
        if os.path.exists(db_path):
            size_bytes = os.path.getsize(db_path)
            if size_bytes < 1024:
                return f"{size_bytes} bytes"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
        return "0 bytes"
    except:
        return "Unknown"

# Login route
@admin_bp.route('/')
def admin_login():
    """Admin login page"""
    if is_admin_logged_in():
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('login.html')

@admin_bp.route('/', methods=['POST'])
def admin_login_post():
    """Handle admin login"""
    password = request.form.get('password')
    
    # Get password from settings if available
    setting = Setting.query.filter_by(key='admin_password').first()
    if setting:
        admin_password = setting.value
    else:
        admin_password = ADMIN_PASSWORD
    
    if password == admin_password:
        session['admin_logged_in'] = True
        flash('Login successful', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    else:
        flash('Invalid password', 'danger')
        return redirect(url_for('admin.admin_login'))

# Logout route
@admin_bp.route('/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    # Redirect to home page instead of login page
    return redirect(url_for('frontend.index'))

# Dashboard route
@admin_bp.route('/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if not is_admin_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    # Get statistics
    stats = {
        'image_count': Image.query.count(),
        'category_count': Category.query.count(),
        'featured_count': FeaturedImage.query.count(),
        'message_count': ContactMessage.query.count(),
        'unread_message_count': ContactMessage.query.filter_by(is_read=False).count(),
        'db_size': get_db_size()
    }
    
    # Get recent images
    recent_images = Image.query.order_by(Image.created_at.desc()).limit(6).all()
    
    # Get recent messages
    recent_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    
    # Get last backup
    last_backup = Backup.query.order_by(Backup.created_at.desc()).first()
    
    # Get current featured image
    current_featured = FeaturedImage.query.filter_by(is_active=True).first()
    
    # Get settings
    settings = {}
    for setting in Setting.query.all():
        settings[setting.key] = setting.value
    
    return render_template('dashboard.html', 
                          stats=stats, 
                          recent_images=recent_images,
                          recent_messages=recent_messages,
                          last_backup=last_backup,
                          current_featured=current_featured,
                          settings=settings)

# Image Management routes
@admin_bp.route('/images')
def image_management():
    """Image management page"""
    if not is_admin_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    category_id = request.args.get('category', None, type=int)
    search = request.args.get('search', None)
    
    # Build query
    query = Image.query
    
    # Filter by category if specified
    if category_id:
        query = query.join(ImageCategory).filter(ImageCategory.category_id == category_id)
    
    # Filter by search term if specified
    if search:
        query = query.filter(
            (Image.title.ilike(f'%{search}%')) | 
            (Image.description.ilike(f'%{search}%'))
        )
    
    # Order by created_at descending
    query = query.order_by(Image.created_at.desc())
    
    # Paginate
    images = query.paginate(page=page, per_page=per_page)
    
    # Get all categories for filter dropdown
    categories = Category.query.order_by(Category.display_order).all()
    
    return render_template('images.html', 
                          images=images,
                          categories=categories,
                          current_category=category_id,
                          search=search)

@admin_bp.route('/images/upload', methods=['GET', 'POST'])
def upload_image():
    """Upload image page"""
    if not is_admin_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'images[]' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        files = request.files.getlist('images[]')
        
        if not files or files[0].filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        
        # Get form data
        title_prefix = request.form.get('title_prefix', '')
        description = request.form.get('description', '')
        category_ids = request.form.getlist('categories')
        
        # Convert category IDs to integers
        category_ids = [int(cat_id) for cat_id in category_ids if cat_id]
        
        # Get categories
        categories = Category.query.filter(Category.id.in_(category_ids)).all()
        
        # Process each file
        success_count = 0
        for file in files:
            if file and allowed_file(file.filename):
                try:
                    # Save file
                    filename = save_uploaded_image(file, 'static')
                    file_path = os.path.join('static', filename)
                    
                    # Extract EXIF data
                    exif_data = extract_exif_data(file_path)
                    
                    # Create image record
                    image = Image(
                        filename=filename,
                        title=f"{title_prefix} {success_count + 1}" if title_prefix else f"Image {success_count + 1}",
                        description=description,
                        camera_make=exif_data.get('camera_make', ''),
                        camera_model=exif_data.get('camera_model', ''),
                        lens=exif_data.get('lens', ''),
                        aperture=exif_data.get('aperture', ''),
                        shutter_speed=exif_data.get('shutter_speed', ''),
                        iso=exif_data.get('iso', 0),
                        focal_length=exif_data.get('focal_length', ''),
                        date_taken=exif_data.get('date_taken', None),
                        is_active=True
                    )
                    
                    # Add to database
                    db.session.add(image)
                    db.session.flush()  # Get image ID
                    
                    # Add categories
                    for category in categories:
                        image_category = ImageCategory(image_id=image.id, category_id=category.id)
                        db.session.add(image_category)
                    
                    success_count += 1
                except Exception as e:
                    flash(f'Error uploading file: {str(e)}', 'danger')
        
        if success_count > 0:
            db.session.commit()
            flash(f'Successfully uploaded {success_count} images', 'success')
        
        return redirect(url_for('admin.image_management'))
    
    # Get all categories for the form
    categories = Category.query.order_by(Category.display_order).all()
    
    return render_template('upload.html', categories=categories)

@admin_bp.route('/images/<int:image_id>/edit', methods=['GET', 'POST'])
def edit_image(image_id):
    """Edit image page"""
    if not is_admin_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    # Get image
    image = Image.query.get_or_404(image_id)
    
    if request.method == 'POST':
        # Update image data
        image.title = request.form.get('title', '')
        image.description = request.form.get('description', '')
        image.camera_make = request.form.get('camera_make', '')
        image.camera_model = request.form.get('camera_model', '')
        image.lens = request.form.get('lens', '')
        image.aperture = request.form.get('aperture', '')
        image.shutter_speed = format_shutter_speed(request.form.get('shutter_speed', ''))
        image.iso = request.form.get('iso', 0)
        image.focal_length = request.form.get('focal_length', '')
        image.location = request.form.get('location', '')
        image.is_active = 'is_active' in request.form
        
        # Update categories
        category_ids = request.form.getlist('categories')
        category_ids = [int(cat_id) for cat_id in category_ids if cat_id]
        
        # Remove all existing categories
        ImageCategory.query.filter_by(image_id=image.id).delete()
        
        # Add new categories
        for cat_id in category_ids:
            image_category = ImageCategory(image_id=image.id, category_id=cat_id)
            db.session.add(image_category)
        
        db.session.commit()
        flash('Image updated successfully', 'success')
        return redirect(url_for('admin.image_management'))
    
    # Get all categories for the form
    categories = Category.query.order_by(Category.display_order).all()
    
    # Get current category IDs
    current_category_ids = [cat.id for cat in image.categories]
    
    return render_template('edit_image.html', 
                          image=image,
                          categories=categories,
                          current_category_ids=current_category_ids)

@admin_bp.route('/images/<int:image_id>/delete', methods=['POST'])
def delete_image(image_id):
    """Delete image"""
    if not is_admin_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    # Get image
    image = Image.query.get_or_404(image_id)
    
    # Delete image file
    try:
        os.remove(os.path.join('static', image.filename))
    except:
        pass
    
    # Delete image record
    db.session.delete(image)
    db.session.commit()
    
    flash('Image deleted successfully', 'success')
    return redirect(url_for('admin.image_management'))

@admin_bp.route('/images/bulk-action', methods=['POST'])
def bulk_image_action():
    """Bulk image actions"""
    if not is_admin_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    action = request.form.get('action')
    image_ids = request.form.getlist('image_ids')
    
    if not image_ids:
        flash('No images selected', 'danger')
        return redirect(url_for('admin.image_management'))
    
    # Convert to integers
    image_ids = [int(id) for id in image_ids]
    
    if action == 'delete':
        # Delete images
        images = Image.query.filter(Image.id.in_(image_ids)).all()
        for image in images:
            # Delete image file
            try:
                os.remove(os.path.join('static', image.filename))
            except:
                pass
            
            # Delete image record
            db.session.delete(image)
        
        db.session.commit()
        flash(f'Successfully deleted {len(images)} images', 'success')
    
    elif action == 'activate':
        # Activate images
        Image.query.filter(Image.id.in_(image_ids)).update({Image.is_active: True}, synchronize_session=False)
        db.session.commit()
        flash(f'Successfully activated {len(image_ids)} images', 'success')
    
    elif action == 'deactivate':
        # Deactivate images
        Image.query.filter(Image.id.in_(image_ids)).update({Image.is_active: False}, synchronize_session=False)
        db.session.commit()
        flash(f'Successfully deactivated {len(image_ids)} images', 'success')
    
    elif action == 'add_category':
        # Add category to images
        category_id = request.form.get('category_id')
        if not category_id:
            flash('No category selected', 'danger')
            return redirect(url_for('admin.image_management'))
        
        category_id = int(category_id)
        
        # Check if category exists
        category = Category.query.get(category_id)
        if not category:
            flash('Category not found', 'danger')
            return redirect(url_for('admin.image_management'))
        
        # Add category to images
        for image_id in image_ids:
            # Check if relationship already exists
            existing = ImageCategory.query.filter_by(image_id=image_id, category_id=category_id).first()
            if not existing:
                image_category = ImageCategory(image_id=image_id, category_id=category_id)
                db.session.add(image_category)
        
        db.session.commit()
        flash(f'Successfully added category "{category.name}" to {len(image_ids)} images', 'success')
    
    elif action == 'remove_category':
        # Remove category from images
        category_id = request.form.get('category_id')
        if not category_id:
            flash('No category selected', 'danger')
            return redirect(url_for('admin.image_management'))
        
        category_id = int(category_id)
        
        # Check if category exists
        category = Category.query.get(category_id)
        if not category:
            flash('Category not found', 'danger')
            return redirect(url_for('admin.image_management'))
        
        # Remove category from images
        ImageCategory.query.filter(
            ImageCategory.image_id.in_(image_ids),
            ImageCategory.category_id == category_id
        ).delete(synchronize_session=False)
        
        db.session.commit()
        flash(f'Successfully removed category "{category.name}" from {len(image_ids)} images', 'success')
    
    return redirect(url_for('admin.image_management'))

# Category Management routes
@admin_bp.route('/categories')
def category_management():
    """Category management page"""
    if not is_admin_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    # Get all categories with image count
    categories = []
    for category in Category.query.order_by(Category.display_order).all():
        image_count = ImageCategory.query.filter_by(category_id=category.id).count()
        category_data = {
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
            'color': category.color_code,
            'description': category.description,
            'display_order': category.display_order,
            'image_count': image_count
        }
        categories.append(category_data)
    
    return render_template('categories.html', categories=categories)

@admin_bp.route('/categories/add', methods=['POST'])
def add_category():
    """Add a new category"""
    if not is_admin_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    name = request.form.get('name')
    slug = request.form.get('slug') or generate_slug(name)
    color_code = request.form.get('color', '#f57931')
    description = request.form.get('description', '')
    
    # Get the highest display_order
    max_order = db.session.query(db.func.max(Category.display_order)).scalar() or 0
    
    # Create new category
    category = Category(
        name=name,
        slug=slug,
        color_code=color_code,
        description=description,
        display_order=max_order + 1
    )
    
    db.session.add(category)
    db.session.commit()
    
    flash(f'Category "{name}" added successfully', 'success')
    return redirect(url_for('admin.category_management'))

@admin_bp.route('/categories/<int:category_id>')
def get_category(category_id):
    """Get category data as JSON"""
    if not is_admin_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    
    category = Category.query.get_or_404(category_id)
    
    return jsonify({
        'id': category.id,
        'name': category.name,
        'slug': category.slug,
        'color_code': category.color_code,
        'description': category.description
    })

@admin_bp.route('/categories/<int:category_id>/edit', methods=['POST'])
def edit_category(category_id):
    """Edit a category"""
    if not is_admin_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    category = Category.query.get_or_404(category_id)
    
    category.name = request.form.get('name')
    category.slug = request.form.get('slug') or generate_slug(category.name)
    category.color_code = request.form.get('color', '#f57931')
    category.description = request.form.get('description', '')
    
    db.session.commit()
    
    flash(f'Category "{category.name}" updated successfully', 'success')
    return redirect(url_for('admin.category_management'))

@admin_bp.route('/categories/<int:category_id>/delete', methods=['POST'])
def delete_category(category_id):
    """Delete a category"""
    if not is_admin_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    category = Category.query.get_or_404(category_id)
    
    # Check if category has images
    image_count = ImageCategory.query.filter_by(category_id=category.id).count()
    if image_count > 0:
        flash(f'Cannot delete category "{category.name}" because it has {image_count} images', 'danger')
        return redirect(url_for('admin.category_management'))
    
    db.session.delete(category)
    db.session.commit()
    
    flash(f'Category "{category.name}" deleted successfully', 'success')
    return redirect(url_for('admin.category_management'))

@admin_bp.route('/categories/reorder', methods=['POST'])
def reorder_categories():
    """Reorder categories"""
    if not is_admin_logged_in():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    category_ids = data.get('category_ids', [])
    
    if not category_ids:
        return jsonify({'error': 'No categories provided'}), 400
    
    # Update display_order for each category
    for i, category_id in enumerate(category_ids):
        category = Category.query.get(category_id)
        if category:
            category.display_order = i
    
    db.session.commit()
    
    return jsonify({'success': True})

# Featured Image routes
@admin_bp.route('/featured')
def featured_management():
    """Featured image management page"""
    if not is_admin_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    # Get all featured images
    featured_images = FeaturedImage.query.order_by(FeaturedImage.start_date.desc()).all()
    
    # Get all images for selection
    images = Image.query.order_by(Image.created_at.desc()).all()
    
    return render_template('featured.html', 
                          featured_images=featured_images,
                          images=images)

@admin_bp.route('/featured/add', methods=['POST'])
def add_featured_image():
    """Add a new featured image"""
    if not is_admin_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    image_id = request.form.get('image_id')
    title = request.form.get('title')
    story = request.form.get('story')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    
    # Convert dates
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except:
        flash('Invalid date format', 'danger')
        return redirect(url_for('admin.featured_management'))
    
    # Check if image exists
    image = Image.query.get(image_id)
    if not image:
        flash('Image not found', 'danger')
        return redirect(url_for('admin.featured_management'))
    
    # Create featured image
    featured_image = FeaturedImage(
        image_id=image_id,
        title=title,
        story=story,
        start_date=start_date,
        end_date=end_date,
        is_active=True
    )
    
    db.session.add(featured_image)
    db.session.commit()
    
    flash('Featured image added successfully', 'success')
    return redirect(url_for('admin.featured_management'))

@admin_bp.route('/featured/<int:featured_id>/edit', methods=['POST'])
def edit_featured_image(featured_id):
    """Edit a featured image"""
    if not is_admin_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    featured_image = FeaturedImage.query.get_or_404(featured_id)
    
    featured_image.title = request.form.get('title')
    featured_image.story = request.form.get('story')
    
    # Convert dates
    try:
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        featured_image.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        featured_image.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except:
        flash('Invalid date format', 'danger')
        return redirect(url_for('admin.featured_management'))
    
    db.session.commit()
    
    flash('Featured image updated successfully', 'success')
    return redirect(url_for('admin.featured_management'))

@admin_bp.route('/featured/<int:featured_id>/delete', methods=['POST'])
def delete_featured_image(featured_id):
    """Delete a featured image"""
    if not is_admin_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    featured_image = FeaturedImage.query.get_or_404(featured_id)
    
    db.session.delete(featured_image)
    db.session.commit()
    
    flash('Featured image deleted successfully', 'success')
    return redirect(url_for('admin.featured_management'))

@admin_bp.route('/featured/<int:featured_id>/toggle', methods=['POST'])
def toggle_featured_image(featured_id):
    """Toggle a featured image active/inactive"""
    if not is_admin_logged_in():
        return redirect(url_for('admin.admin_login'))
    
    featured_image = FeaturedImage.query.get_or_404(featured_id)
    
    featured_image.is_active = not featured_image.is_active
    
    db.session.commit()
    
    status = 'activated' if featured_image.is_active else 'deactivated'
    flash(f'Featured image {status} successfully', 'success')
    return redirect(url_for('admin.featured_management'))

