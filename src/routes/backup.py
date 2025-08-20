import os
import zipfile
import tempfile
from datetime import datetime
import shutil
from flask import Blueprint, render_template, session, redirect, url_for, jsonify, send_file

backup_bp = Blueprint('backup', __name__)

def get_directory_size(directory):
    """Calculate the total size of a directory in bytes"""
    total_size = 0
    try:
        if os.path.exists(directory) and os.access(directory, os.R_OK):
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                    except (OSError, IOError):
                        continue
    except Exception:
        pass
    return total_size

def get_backup_stats():
    """Get statistics for the backup dashboard"""
    try:
        # Photography assets directory
        photography_assets_dir = '/home/Heur1konrc/photography-assets'
        
        # Check if directory exists and is readable
        photo_exists = os.path.exists(photography_assets_dir)
        photo_readable = os.access(photography_assets_dir, os.R_OK) if photo_exists else False
        
        # Count photography assets and calculate size
        photography_assets_count = 0
        photography_assets_size = 0  # Keep as number (bytes)
        
        if photo_exists and photo_readable:
            photography_assets_size = get_directory_size(photography_assets_dir)
            try:
                for root, dirs, files in os.walk(photography_assets_dir):
                    for file in files:
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.tiff', '.bmp', '.webp')):
                            photography_assets_count += 1
            except Exception:
                pass
        
        # Website files directory
        website_dir = '/home/Heur1konrc/minds-eye-photography'
        website_files_count = 0
        website_size = 0  # Keep as number (bytes)
        
        if os.path.exists(website_dir):
            website_size = get_directory_size(website_dir)
            try:
                for root, dirs, files in os.walk(website_dir):
                    # Skip virtual environment and cache directories
                    if any(skip_dir in root for skip_dir in ['venv', '__pycache__', '.git']):
                        continue
                    website_files_count += len(files)
            except Exception:
                pass
        
        # Database files
        database_dir = os.path.join(website_dir, 'src', 'database')
        database_files_count = 0
        database_size = 0  # Keep as number (bytes)
        
        if os.path.exists(database_dir):
            database_size = get_directory_size(database_dir)
            try:
                database_files_count = len([f for f in os.listdir(database_dir) if os.path.isfile(os.path.join(database_dir, f))])
            except Exception:
                pass
        
        # Calculate total size (keep as number)
        total_size = photography_assets_size + website_size + database_size
        
        # Create debug info string
        debug_info = f"Photo dir exists: {photo_exists}, readable: {photo_readable}, count: {photography_assets_count}, size: {photography_assets_size} bytes"
        
        return {
            'photography_assets_count': photography_assets_count,
            'photography_assets_size': photography_assets_size,  # NUMBER in bytes
            'website_files_count': website_files_count,
            'website_size': website_size,  # NUMBER in bytes
            'database_files_count': database_files_count,
            'database_size': database_size,  # NUMBER in bytes
            'total_files': photography_assets_count + website_files_count + database_files_count,
            'total_size': total_size,  # NUMBER in bytes
            'last_backup': debug_info,  # Debug info as string
            'backup_size': total_size  # NUMBER in bytes
        }
    except Exception as e:
        # Return error info in stats
        return {
            'photography_assets_count': 0,
            'photography_assets_size': 0,
            'website_files_count': 0,
            'website_size': 0,
            'database_files_count': 0,
            'database_size': 0,
            'total_files': 0,
            'total_size': 0,
            'last_backup': f'Error: {str(e)}',
            'backup_size': 0
        }

@backup_bp.route('/admin/backup')
def backup_admin():
    """Backup admin interface with real data"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))
    
    # Get real backup statistics
    stats = get_backup_stats()
    
    # Pass stats with BOTH variable names
    return render_template('backup_admin.html', 
                         stats=stats, 
                         portfolio_stats=stats)

@backup_bp.route('/admin/backup/create', methods=['POST'])
def create_backup():
    """Create a backup of the portfolio and website"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Create temporary file for backup
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        temp_file.close()
        
        # Create backup ZIP
        with zipfile.ZipFile(temp_file.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Backup photography assets
            photography_assets_dir = '/home/Heur1konrc/photography-assets'
            if os.path.exists(photography_assets_dir):
                for root, dirs, files in os.walk(photography_assets_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Create archive path relative to parent directory
                        arcname = os.path.relpath(file_path, os.path.dirname(photography_assets_dir))
                        zipf.write(file_path, arcname)
            
            # Backup website data (excluding venv and __pycache__)
            website_dir = '/home/Heur1konrc/minds-eye-photography'
            if os.path.exists(website_dir):
                for root, dirs, files in os.walk(website_dir):
                    # Skip virtual environment and cache directories
                    dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git']]
                    
                    for file in files:
                        if not file.endswith('.pyc'):
                            file_path = os.path.join(root, file)
                            # Create archive path with website-data prefix
                            arcname = os.path.join('website-data', os.path.relpath(file_path, website_dir))
                            zipf.write(file_path, arcname)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'minds_eye_photography_backup_{timestamp}.zip'
        
        # Return the backup file for download
        return send_file(temp_file.name, 
                        as_attachment=True, 
                        download_name=backup_filename,
                        mimetype='application/zip')
    
    except Exception as e:
        return jsonify({'error': f'Backup creation failed: {str(e)}'}), 500

@backup_bp.route('/admin/backup/status')
def backup_status():
    """Get backup status for AJAX updates"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    stats = get_backup_stats()
    return jsonify(stats)

