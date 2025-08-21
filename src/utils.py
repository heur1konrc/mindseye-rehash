import os
import uuid
from datetime import datetime
from PIL import Image as PILImage
from PIL.ExifTags import TAGS
import re

def save_uploaded_image(file, upload_folder):
    """Save uploaded image and return filename"""
    # Generate unique filename
    filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1].lower()
    file_path = os.path.join(upload_folder, filename)
    
    # Save file
    file.save(file_path)
    
    return filename

def extract_exif_data(file_path):
    """Extract EXIF data from image file"""
    try:
        image = PILImage.open(file_path)
        exif_data = {}
        
        if hasattr(image, '_getexif') and image._getexif():
            exif = image._getexif()
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                exif_data[tag] = value
        
        # Extract common camera information
        camera_make = exif_data.get('Make', '')
        camera_model = exif_data.get('Model', '')
        
        # Clean up camera make/model to avoid redundancy
        if camera_model.startswith(camera_make):
            camera_model = camera_model[len(camera_make):].strip()
        
        # Extract lens information
        lens = exif_data.get('LensModel', '')
        
        # Extract aperture (f-stop)
        aperture = None
        if 'FNumber' in exif_data:
            aperture_value = exif_data['FNumber']
            if isinstance(aperture_value, tuple) and len(aperture_value) == 2:
                aperture = f"f/{aperture_value[0]/aperture_value[1]:.1f}"
            else:
                aperture = f"f/{float(aperture_value):.1f}"
        
        # Extract shutter speed as fraction
        shutter_speed = None
        if 'ExposureTime' in exif_data:
            exposure = exif_data['ExposureTime']
            if isinstance(exposure, tuple) and len(exposure) == 2:
                if exposure[0] == 1:
                    shutter_speed = f"1/{exposure[1]}"
                else:
                    shutter_speed = f"{exposure[0]}/{exposure[1]}"
            elif isinstance(exposure, float):
                # Convert decimal to fraction
                if exposure >= 1:
                    shutter_speed = str(int(exposure))
                else:
                    denominator = int(1/exposure)
                    shutter_speed = f"1/{denominator}"
        
        # Extract ISO
        iso = exif_data.get('ISOSpeedRatings', 0)
        
        # Extract focal length
        focal_length = None
        if 'FocalLength' in exif_data:
            fl = exif_data['FocalLength']
            if isinstance(fl, tuple) and len(fl) == 2:
                focal_length = f"{fl[0]/fl[1]}mm"
            else:
                focal_length = f"{fl}mm"
        
        # Extract date taken
        date_taken = None
        if 'DateTimeOriginal' in exif_data:
            date_str = exif_data['DateTimeOriginal']
            try:
                date_taken = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
            except:
                pass
        
        return {
            'camera_make': camera_make,
            'camera_model': camera_model,
            'lens': lens,
            'aperture': aperture,
            'shutter_speed': shutter_speed,
            'iso': iso,
            'focal_length': focal_length,
            'date_taken': date_taken
        }
    except Exception as e:
        print(f"Error extracting EXIF data: {e}")
        return {}

def format_shutter_speed(value):
    """Format shutter speed as a fraction"""
    if not value:
        return None
    
    # If already in fraction format, return as is
    if '/' in str(value):
        return value
    
    # Convert decimal to fraction
    try:
        float_value = float(value)
        if float_value >= 1:
            return str(int(float_value))
        else:
            denominator = int(1/float_value)
            return f"1/{denominator}"
    except:
        return value

def generate_slug(text):
    """Generate URL-friendly slug from text"""
    # Convert to lowercase
    slug = text.lower()
    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)
    # Remove non-alphanumeric characters
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    # Remove multiple hyphens
    slug = re.sub(r'-+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    return slug

def create_backup(db_path, backup_dir):
    """Create backup of database"""
    import shutil
    import time
    
    # Create backup directory if it doesn't exist
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    backup_filename = f"mindseye_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    # Copy database file
    try:
        shutil.copy2(db_path, backup_path)
        file_size = os.path.getsize(backup_path)
        return {
            'filename': backup_filename,
            'path': backup_path,
            'size_bytes': file_size,
            'success': True
        }
    except Exception as e:
        print(f"Backup failed: {e}")
        return {
            'filename': backup_filename,
            'path': None,
            'size_bytes': 0,
            'success': False
        }

def restore_backup(backup_path, db_path):
    """Restore database from backup"""
    import shutil
    
    try:
        # Create backup of current database first
        current_backup = create_backup(db_path, os.path.dirname(db_path))
        
        # Restore from backup
        shutil.copy2(backup_path, db_path)
        return True
    except Exception as e:
        print(f"Restore failed: {e}")
        return False

