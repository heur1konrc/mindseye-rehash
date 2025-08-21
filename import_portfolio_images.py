"""
Script to import portfolio images from static/portfolio.json to the admin database
"""
import os
import sys
import json
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Sample images data
def import_portfolio_images():
    """Import portfolio images from static/portfolio.json to the admin database"""
    # Create database engine
    engine = create_engine('sqlite:////home/ubuntu/mindseye-rehash/src/database/mindseye.db')
    conn = engine.connect()
    
    # Load portfolio.json
    try:
        with open('/home/ubuntu/mindseye-rehash/src/static/portfolio.json', 'r') as f:
            portfolio_data = json.load(f)
    except Exception as e:
        print(f"Error loading portfolio.json: {e}")
        return False
    
    # Get existing categories or create them
    categories = {}
    for category_name in ['Landscapes', 'Wildlife', 'Nature', 'Portraits', 'Events', 'Flora', 'Pets']:
        # Check if category exists
        result = conn.execute(text("SELECT id FROM categories WHERE name = :name"), {"name": category_name})
        category = result.fetchone()
        
        if not category:
            # Create new category
            result = conn.execute(
                text("INSERT INTO categories (name, slug, description, color_code, is_active, created_at) VALUES (:name, :slug, :description, :color_code, :is_active, :created_at)"),
                {
                    "name": category_name,
                    "slug": category_name.lower(),
                    "description": f"{category_name} photography",
                    "color_code": "#f57931",
                    "is_active": True,
                    "created_at": datetime.now()
                }
            )
            conn.commit()
            
            # Get the new category ID
            result = conn.execute(text("SELECT id FROM categories WHERE name = :name"), {"name": category_name})
            category = result.fetchone()
        
        categories[category_name] = category[0]
    
    # Import images from portfolio.json
    images = portfolio_data.get('images', [])
    for img_data in images:
        # Check if image already exists
        filename = img_data.get('filename', '')
        if not filename:
            continue
            
        result = conn.execute(text("SELECT id FROM images WHERE filename = :filename"), {"filename": filename})
        existing_image = result.fetchone()
        
        if existing_image:
            print(f"Image {filename} already exists, skipping...")
            continue
        
        # Create new image
        result = conn.execute(
            text("""
                INSERT INTO images (
                    filename, title, description, camera_make, camera_model, 
                    lens, aperture, shutter_speed, iso, focal_length, 
                    location, is_active, created_at, updated_at
                ) VALUES (
                    :filename, :title, :description, :camera_make, :camera_model,
                    :lens, :aperture, :shutter_speed, :iso, :focal_length,
                    :location, :is_active, :created_at, :updated_at
                )
            """),
            {
                "filename": filename,
                "title": img_data.get('title', 'Untitled'),
                "description": img_data.get('description', ''),
                "camera_make": img_data.get('camera_make', ''),
                "camera_model": img_data.get('camera_model', ''),
                "lens": img_data.get('lens', ''),
                "aperture": img_data.get('aperture', ''),
                "shutter_speed": img_data.get('shutter_speed', ''),
                "iso": img_data.get('iso', 0),
                "focal_length": img_data.get('focal_length', ''),
                "location": img_data.get('location', ''),
                "is_active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        )
        conn.commit()
        
        # Get the new image ID
        result = conn.execute(text("SELECT id FROM images WHERE filename = :filename"), {"filename": filename})
        image_id = result.fetchone()[0]
        
        # Add categories
        img_categories = img_data.get('categories', [])
        for cat_data in img_categories:
            category_name = cat_data.get('name', '')
            if not category_name or category_name not in categories:
                continue
                
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
        
        print(f"Added image: {filename}")
    
    # Close connection
    conn.close()
    print("Portfolio images imported successfully!")
    return True

if __name__ == "__main__":
    import_portfolio_images()

