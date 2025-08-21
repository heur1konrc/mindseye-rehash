"""
Script to add sample images to the database
"""
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Sample images data
sample_images = [
    {
        'filename': 'sample_images/sunset_lake.png',
        'title': 'Sunset Over Mountain Lake',
        'description': 'A breathtaking sunset captured over a tranquil mountain lake, with silhouettes of trees and mountains creating a dramatic backdrop.',
        'categories': ['Landscapes', 'Nature']
    },
    {
        'filename': 'sample_images/eagle_flight.png',
        'title': 'Bald Eagle in Flight',
        'description': 'A majestic bald eagle soaring through a clear blue sky, showcasing its impressive wingspan and powerful presence.',
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
        result = conn.execute(text("SELECT id FROM portfolio_images WHERE filename = :filename"), {"filename": img_data['filename']})
        existing_image = result.fetchone()
        
        if existing_image:
            print(f"Image {img_data['title']} already exists, skipping...")
            continue
        
        # Create new image
        result = conn.execute(
            text("""
                INSERT INTO portfolio_images (
                    filename, title, description, is_active, created_at
                ) VALUES (
                    :filename, :title, :description, :is_active, :created_at
                )
            """),
            {
                "filename": img_data['filename'],
                "title": img_data['title'],
                "description": img_data['description'],
                "is_active": True,
                "created_at": datetime.now()
            }
        )
        conn.commit()
        
        # Get the new image ID
        result = conn.execute(text("SELECT id FROM portfolio_images WHERE filename = :filename"), {"filename": img_data['filename']})
        image_id = result.fetchone()[0]
        
        # Add categories
        for category_name in img_data['categories']:
            if category_name in categories:
                # Check if relationship already exists
                result = conn.execute(
                    text("SELECT image_id, category_id FROM image_categories WHERE image_id = :image_id AND category_id = :category_id"),
                    {"image_id": image_id, "category_id": categories[category_name]}
                )
                if not result.fetchone():
                    # Create new relationship
                    conn.execute(
                        text("INSERT INTO image_categories (image_id, category_id) VALUES (:image_id, :category_id)"),
                        {
                            "image_id": image_id,
                            "category_id": categories[category_name]
                        }
                    )
                    conn.commit()
        
        print(f"Added image: {img_data['title']}")
    
    # Close connection
    conn.close()
    print("Sample images added successfully!")

if __name__ == "__main__":
    add_sample_images()

