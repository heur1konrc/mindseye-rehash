from flask import Blueprint, jsonify, request
import os
import json
import logging
from models import db, Image, Category, FeaturedImage, ContactMessage

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/portfolio', methods=['GET'])
def get_portfolio():
    """Get all portfolio images and categories"""
    try:
        # Get all images
        images = Image.query.all()
        image_list = []
        
        for image in images:
            # Get categories for this image
            categories = []
            for category in image.categories:
                categories.append({
                    'id': category.id,
                    'name': category.name,
                    'slug': category.slug,
                    'color_code': category.color_code
                })
            
            # Add image to list
            image_list.append({
                'id': image.id,
                'title': image.title,
                'description': image.description,
                'image_path': image.image_path,
                'camera': image.camera,
                'lens': image.lens,
                'aperture': image.aperture,
                'shutter_speed': image.shutter_speed,
                'iso': image.iso,
                'focal_length': image.focal_length,
                'categories': categories
            })
        
        # Get all categories
        categories = Category.query.all()
        category_list = []
        
        for category in categories:
            category_list.append({
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'color_code': category.color_code
            })
        
        return jsonify({
            'images': image_list,
            'categories': category_list
        })
    
    except Exception as e:
        logger.error(f"Error getting portfolio: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/featured', methods=['GET'])
def get_featured():
    """Get the current featured image"""
    try:
        # Get the current featured image
        featured = FeaturedImage.query.order_by(FeaturedImage.start_date.desc()).first()
        
        if featured:
            # Get the image
            image = Image.query.get(featured.image_id)
            
            if image:
                # Get categories for this image
                categories = []
                for category in image.categories:
                    categories.append({
                        'id': category.id,
                        'name': category.name,
                        'slug': category.slug,
                        'color_code': category.color_code
                    })
                
                # Return featured image data
                return jsonify({
                    'featured': {
                        'id': featured.id,
                        'title': image.title,
                        'description': image.description,
                        'story': featured.story,
                        'image_path': image.image_path,
                        'camera': image.camera,
                        'lens': image.lens,
                        'aperture': image.aperture,
                        'shutter_speed': image.shutter_speed,
                        'iso': image.iso,
                        'focal_length': image.focal_length,
                        'start_date': featured.start_date.strftime('%Y-%m-%d'),
                        'end_date': featured.end_date.strftime('%Y-%m-%d') if featured.end_date else None,
                        'categories': categories
                    }
                })
        
        # If no featured image, return empty data
        return jsonify({'featured': None})
    
    except Exception as e:
        logger.error(f"Error getting featured image: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/contact', methods=['POST'])
def submit_contact():
    """Submit a contact form"""
    try:
        # Get form data
        data = request.get_json()
        
        # Create new contact message
        message = ContactMessage(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            subject=data.get('subject'),
            message=data.get('message')
        )
        
        # Save to database
        db.session.add(message)
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        logger.error(f"Error submitting contact form: {str(e)}")
        return jsonify({'error': str(e)}), 500

# For development/testing - load sample data if database is empty
@api_bp.route('/sample-data', methods=['GET'])
def load_sample_data():
    """Load sample data for development/testing"""
    try:
        # Check if database is empty
        if Image.query.count() == 0:
            # Create sample categories
            categories = [
                Category(name='Landscapes', slug='landscapes', color_code='#4CAF50'),
                Category(name='Wildlife', slug='wildlife', color_code='#FF9800'),
                Category(name='Portraits', slug='portraits', color_code='#2196F3'),
                Category(name='Events', slug='events', color_code='#9C27B0'),
                Category(name='Nature', slug='nature', color_code='#8BC34A')
            ]
            
            for category in categories:
                db.session.add(category)
            
            db.session.commit()
            
            # Create sample images
            images = [
                {
                    'title': 'Sunset at Lake Monona',
                    'description': 'Beautiful sunset over Lake Monona in Madison',
                    'image_path': '/static/sample_images/sunset_lake.png',
                    'camera': 'Canon EOS R8',
                    'lens': 'RF 24-105mm f/4L IS USM',
                    'aperture': 'f/8.0',
                    'shutter_speed': '1/125',
                    'iso': '100',
                    'focal_length': '35mm',
                    'categories': ['landscapes', 'nature']
                },
                {
                    'title': 'Bald Eagle in Flight',
                    'description': 'Majestic bald eagle soaring against a blue sky',
                    'image_path': '/static/sample_images/eagle_flight.png',
                    'camera': 'Canon EOS R8',
                    'lens': 'RF 100-500mm f/4.5-7.1L IS USM',
                    'aperture': 'f/5.6',
                    'shutter_speed': '1/2000',
                    'iso': '400',
                    'focal_length': '500mm',
                    'categories': ['wildlife', 'nature']
                }
            ]
            
            for img_data in images:
                # Create image
                image = Image(
                    title=img_data['title'],
                    description=img_data['description'],
                    image_path=img_data['image_path'],
                    camera=img_data['camera'],
                    lens=img_data['lens'],
                    aperture=img_data['aperture'],
                    shutter_speed=img_data['shutter_speed'],
                    iso=img_data['iso'],
                    focal_length=img_data['focal_length']
                )
                
                db.session.add(image)
                db.session.flush()  # Get the image ID
                
                # Add categories
                for cat_slug in img_data['categories']:
                    category = Category.query.filter_by(slug=cat_slug).first()
                    if category:
                        image.categories.append(category)
            
            # Create featured image
            if images:
                image = Image.query.first()
                if image:
                    featured = FeaturedImage(
                        image_id=image.id,
                        story="This image was captured during a perfect summer evening at Lake Monona in Madison. I had been waiting for weeks for the perfect conditions - clear skies with just enough clouds to catch the colors of sunset. As the sun began to dip below the horizon, the entire sky erupted in vibrant oranges and purples, reflecting perfectly in the calm waters of the lake.",
                        start_date='2025-08-01',
                        end_date='2025-08-31'
                    )
                    db.session.add(featured)
            
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Sample data loaded successfully'})
        
        return jsonify({'success': False, 'message': 'Database is not empty'})
    
    except Exception as e:
        logger.error(f"Error loading sample data: {str(e)}")
        return jsonify({'error': str(e)}), 500

