from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os

db = SQLAlchemy()

class Image(db.Model):
    """Image model for storing photography images"""
    __tablename__ = 'images'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    camera_make = db.Column(db.String(100), nullable=True)
    camera_model = db.Column(db.String(100), nullable=True)
    lens = db.Column(db.String(100), nullable=True)
    aperture = db.Column(db.String(20), nullable=True)
    shutter_speed = db.Column(db.String(20), nullable=True)  # Store as fraction (e.g., "1/500")
    iso = db.Column(db.Integer, nullable=True)
    focal_length = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    date_taken = db.Column(db.DateTime, nullable=True)
    date_uploaded = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    view_count = db.Column(db.Integer, default=0)
    download_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    categories = db.relationship('Category', secondary='image_categories', back_populates='images')
    featured_images = db.relationship('FeaturedImage', back_populates='image')
    background_settings = db.relationship('BackgroundSetting', back_populates='image')
    
    def to_dict(self):
        """Convert image to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'title': self.title,
            'description': self.description,
            'camera_make': self.camera_make,
            'camera_model': self.camera_model,
            'camera_display': f"{self.camera_make} {self.camera_model}" if self.camera_make and self.camera_model else None,
            'lens': self.lens,
            'aperture': self.aperture,
            'shutter_speed': self.shutter_speed,  # Already stored as fraction
            'iso': self.iso,
            'focal_length': self.focal_length,
            'location': self.location,
            'date_taken': self.date_taken.isoformat() if self.date_taken else None,
            'date_uploaded': self.date_uploaded.isoformat(),
            'is_active': self.is_active,
            'view_count': self.view_count,
            'download_count': self.download_count,
            'categories': [category.to_dict() for category in self.categories],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Category(db.Model):
    """Category model for organizing images"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    color_code = db.Column(db.String(7), default='#f57931')  # Default to brand orange
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    images = db.relationship('Image', secondary='image_categories', back_populates='categories')
    
    def to_dict(self):
        """Convert category to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'color_code': self.color_code,
            'display_order': self.display_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class ImageCategory(db.Model):
    """Junction table for many-to-many relationship between images and categories"""
    __tablename__ = 'image_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent duplicate assignments
    __table_args__ = (db.UniqueConstraint('image_id', 'category_id', name='uix_image_category'),)


class FeaturedImage(db.Model):
    """Featured image model for weekly featured images with story blocks"""
    __tablename__ = 'featured_images'
    
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=True)
    story = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    image = db.relationship('Image', back_populates='featured_images')
    
    def to_dict(self):
        """Convert featured image to dictionary"""
        return {
            'id': self.id,
            'image_id': self.image_id,
            'title': self.title or self.image.title,
            'story': self.story,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'is_active': self.is_active,
            'image': self.image.to_dict(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class BackgroundSetting(db.Model):
    """Background setting model for website section backgrounds"""
    __tablename__ = 'background_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(50), nullable=False, unique=True)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id', ondelete='SET NULL'), nullable=True)
    color_code = db.Column(db.String(7), default='#19114f')  # Default to brand blue
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    image = db.relationship('Image', back_populates='background_settings')
    
    def to_dict(self):
        """Convert background setting to dictionary"""
        return {
            'id': self.id,
            'section': self.section,
            'image_id': self.image_id,
            'color_code': self.color_code,
            'is_active': self.is_active,
            'image': self.image.to_dict() if self.image else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class ContactMessage(db.Model):
    """Contact message model for storing contact form submissions"""
    __tablename__ = 'contact_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(255), nullable=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert contact message to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'subject': self.subject,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }


class Backup(db.Model):
    """Backup model for tracking backup history"""
    __tablename__ = 'backups'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    size_bytes = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'manual' or 'automatic'
    status = db.Column(db.String(20), nullable=False)  # 'success' or 'failed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert backup to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'size_bytes': self.size_bytes,
            'type': self.type,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }


class Setting(db.Model):
    """Setting model for storing general website settings"""
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), nullable=False, unique=True)
    value = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert setting to dictionary"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


# Helper functions for database operations
def init_db(app):
    """Initialize database with app context"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        create_default_data()


def create_default_data():
    """Create default data if tables are empty"""
    # Create default categories if none exist
    if Category.query.count() == 0:
        default_categories = [
            {'name': 'Wildlife', 'slug': 'wildlife', 'display_order': 1},
            {'name': 'Landscapes', 'slug': 'landscapes', 'display_order': 2},
            {'name': 'Portraits', 'slug': 'portraits', 'display_order': 3},
            {'name': 'Events', 'slug': 'events', 'display_order': 4},
            {'name': 'Nature', 'slug': 'nature', 'display_order': 5},
            {'name': 'Macro', 'slug': 'macro', 'display_order': 6},
            {'name': 'Architecture', 'slug': 'architecture', 'display_order': 7},
            {'name': 'Street', 'slug': 'street', 'display_order': 8}
        ]
        
        for cat_data in default_categories:
            category = Category(
                name=cat_data['name'],
                slug=cat_data['slug'],
                display_order=cat_data['display_order']
            )
            db.session.add(category)
        
        db.session.commit()
    
    # Create default settings if none exist
    if Setting.query.count() == 0:
        default_settings = [
            {'key': 'site_name', 'value': "Mind's Eye Photography"},
            {'key': 'site_tagline', 'value': "Where Moments Meet Imagination"},
            {'key': 'admin_email', 'value': "info@themindseyestudio.com"},
            {'key': 'items_per_page', 'value': "12"},
            {'key': 'enable_auto_backup', 'value': "true"},
            {'key': 'backup_retention_days', 'value': "7"},
            {'key': 'primary_color', 'value': "#f57931"},  # Brand orange
            {'key': 'background_color', 'value': "#19114f"}  # Brand blue
        ]
        
        for setting_data in default_settings:
            setting = Setting(
                key=setting_data['key'],
                value=setting_data['value']
            )
            db.session.add(setting)
        
        db.session.commit()
    
    # Create default background settings if none exist
    if BackgroundSetting.query.count() == 0:
        default_sections = ['home', 'portfolio', 'featured', 'about', 'contact']
        
        for section in default_sections:
            bg_setting = BackgroundSetting(
                section=section,
                color_code='#19114f'  # Brand blue
            )
            db.session.add(bg_setting)
        
        db.session.commit()


def import_legacy_data(json_file_path):
    """Import legacy data from JSON file"""
    if not os.path.exists(json_file_path):
        return False
    
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        
        # Import images
        images_data = data.get('images', [])
        for img_data in images_data:
            # Check if image already exists
            existing_image = Image.query.filter_by(filename=img_data.get('filename')).first()
            if existing_image:
                continue
            
            # Create new image
            image = Image(
                filename=img_data.get('filename'),
                title=img_data.get('title', 'Untitled'),
                description=img_data.get('description', ''),
                camera_make=img_data.get('camera_make', ''),
                camera_model=img_data.get('camera_model', ''),
                lens=img_data.get('lens', ''),
                aperture=img_data.get('aperture', ''),
                shutter_speed=img_data.get('shutter_speed', ''),
                iso=img_data.get('iso', 0),
                is_active=True
            )
            db.session.add(image)
            db.session.flush()  # Get image ID
            
            # Add categories
            categories_data = img_data.get('categories', [])
            for cat_data in categories_data:
                cat_name = cat_data.get('name', '')
                if not cat_name:
                    continue
                
                # Find or create category
                category = Category.query.filter_by(name=cat_name).first()
                if not category:
                    slug = cat_name.lower().replace(' ', '-')
                    category = Category(name=cat_name, slug=slug)
                    db.session.add(category)
                    db.session.flush()  # Get category ID
                
                # Create image-category relationship
                image_category = ImageCategory(image_id=image.id, category_id=category.id)
                db.session.add(image_category)
        
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error importing legacy data: {e}")
        return False

