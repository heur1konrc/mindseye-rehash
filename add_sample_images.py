"""
Script to add sample images to the database
"""
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import models
from src.models import db, Image, Category, ImageCategory

# Sample images data
sample_images = [
    {
        'filename': 'sample_images/sunset_lake.png',
        'title': 'Sunset Over Mountain Lake',
        'description': 'A breathtaking sunset captured over a tranquil mountain lake, with silhouettes of trees and mountains creating a dramatic backdrop.',
        'camera_make': 'Canon',
        'camera_model': 'EOS R8',
        'lens': 'RF 24-70mm f/2.8L IS USM',
        'aperture': 'f/8',
        'shutter_speed': '1/125',
        'iso': 100,
        'focal_length': '35mm',
        'location': 'Lake Monona, Wisconsin',
        'categories': ['Landscapes', 'Nature']
    },
    {
        'filename': 'sample_images/eagle_flight.png',
        'title': 'Bald Eagle in Flight',
        'description': 'A majestic bald eagle soaring through a clear blue sky, showcasing its impressive wingspan and powerful presence.',
        'camera_make': 'Nikon',
        'camera_model': 'Z9',
        'lens': 'NIKKOR Z 100-400mm f/4.5-5.6 VR S',
        'aperture': 'f/5.6',
        'shutter_speed': '1/2000',
        'iso': 400,
        'focal_length': '400mm',
        'location': 'Eagle River, Wisconsin',
        'categories': ['Wildlife', 'Nature']
    }
]

def add_sample_images():
    """Add sample images to the database"""
    # Create database engine
    engine = create_engine('sqlite:///src/database/app.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Get existing categories or create them
    categories = {}
    for category_name in ['Landscapes', 'Wildlife', 'Nature', 'Portraits']:
        category = session.query(Category).filter_by(name=category_name).first()
        if not category:
            category = Category(
                name=category_name,
                slug=category_name.lower(),
                color_code='#f57931',
                display_order=len(categories) + 1
            )
            session.add(category)
            session.flush()
        categories[category_name] = category
    
    # Add sample images
    for img_data in sample_images:
        # Check if image already exists
        existing_image = session.query(Image).filter_by(filename=img_data['filename']).first()
        if existing_image:
            print(f"Image {img_data['title']} already exists, skipping...")
            continue
        
        # Create new image
        image = Image(
            filename=img_data['filename'],
            title=img_data['title'],
            description=img_data['description'],
            camera_make=img_data['camera_make'],
            camera_model=img_data['camera_model'],
            lens=img_data['lens'],
            aperture=img_data['aperture'],
            shutter_speed=img_data['shutter_speed'],
            iso=img_data['iso'],
            focal_length=img_data['focal_length'],
            location=img_data['location'],
            date_taken=datetime.now(),
            date_uploaded=datetime.now(),
            is_active=True
        )
        session.add(image)
        session.flush()
        
        # Add categories
        for category_name in img_data['categories']:
            if category_name in categories:
                image_category = ImageCategory(
                    image_id=image.id,
                    category_id=categories[category_name].id
                )
                session.add(image_category)
        
        print(f"Added image: {img_data['title']}")
    
    # Commit changes
    session.commit()
    print("Sample images added successfully!")

if __name__ == "__main__":
    add_sample_images()

