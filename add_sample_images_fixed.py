"""
Script to add sample images to the database
"""
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    conn = engine.connect()
    
    # Get existing categories or create them
    categories = {}
    for category_name in ['Landscapes', 'Wildlife', 'Nature', 'Portraits']:
        # Check if category exists
        result = conn.execute(text("SELECT id FROM categories WHERE name = :name"), {"name": category_name})
        category = result.fetchone()
        
        if not category:
            # Create new category
            result = conn.execute(
                text("INSERT INTO categories (name, description, is_active, created_at) VALUES (:name, :description, :is_active, :created_at)"),
                {
                    "name": category_name,
                    "description": f"{category_name} photography",
                    "is_active": True,
                    "created_at": datetime.now()
                }
            )
            conn.commit()
            
            # Get the new category ID
            result = conn.execute(text("SELECT id FROM categories WHERE name = :name"), {"name": category_name})
            category = result.fetchone()
        
        categories[category_name] = category[0]
    
    # Add sample images
    for img_data in sample_images:
        # Check if image already exists
        result = conn.execute(text("SELECT id FROM images WHERE filename = :filename"), {"filename": img_data['filename']})
        existing_image = result.fetchone()
        
        if existing_image:
            print(f"Image {img_data['title']} already exists, skipping...")
            continue
        
        # Create new image
        result = conn.execute(
            text("""
                INSERT INTO images (
                    filename, title, description, camera_make, camera_model, 
                    lens, aperture, shutter_speed, iso, focal_length, 
                    location, date_taken, date_uploaded, is_active, created_at
                ) VALUES (
                    :filename, :title, :description, :camera_make, :camera_model,
                    :lens, :aperture, :shutter_speed, :iso, :focal_length,
                    :location, :date_taken, :date_uploaded, :is_active, :created_at
                )
            """),
            {
                "filename": img_data['filename'],
                "title": img_data['title'],
                "description": img_data['description'],
                "camera_make": img_data['camera_make'],
                "camera_model": img_data['camera_model'],
                "lens": img_data['lens'],
                "aperture": img_data['aperture'],
                "shutter_speed": img_data['shutter_speed'],
                "iso": img_data['iso'],
                "focal_length": img_data['focal_length'],
                "location": img_data['location'],
                "date_taken": datetime.now(),
                "date_uploaded": datetime.now(),
                "is_active": True,
                "created_at": datetime.now()
            }
        )
        conn.commit()
        
        # Get the new image ID
        result = conn.execute(text("SELECT id FROM images WHERE filename = :filename"), {"filename": img_data['filename']})
        image_id = result.fetchone()[0]
        
        # Add categories
        for category_name in img_data['categories']:
            if category_name in categories:
                # Check if relationship already exists
                result = conn.execute(
                    text("SELECT id FROM image_categories WHERE image_id = :image_id AND category_id = :category_id"),
                    {"image_id": image_id, "category_id": categories[category_name]}
                )
                if not result.fetchone():
                    # Create new relationship
                    conn.execute(
                        text("INSERT INTO image_categories (image_id, category_id, created_at) VALUES (:image_id, :category_id, :created_at)"),
                        {
                            "image_id": image_id,
                            "category_id": categories[category_name],
                            "created_at": datetime.now()
                        }
                    )
                    conn.commit()
        
        print(f"Added image: {img_data['title']}")
    
    # Close connection
    conn.close()
    print("Sample images added successfully!")

if __name__ == "__main__":
    add_sample_images()

