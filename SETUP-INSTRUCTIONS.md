# Mind's Eye Photography - PythonAnywhere Setup

## Quick Setup Instructions

### Step 1: Upload Files
1. Create folder: `/home/yourusername/minds-eye-photography/`
2. Upload all files from this package to that folder
3. Maintain the directory structure exactly as provided

### Step 2: Install Dependencies
```bash
cd minds-eye-photography
pip3.10 install --user -r requirements.txt
```

### Step 3: Create Web App
1. Go to Web tab in PythonAnywhere
2. Add new web app → Manual configuration → Python 3.10
3. Set source code: `/home/yourusername/minds-eye-photography/src`
4. Configure WSGI file: Use the provided `pythonanywhere_wsgi.py`
5. Update the username in WSGI file: Replace "yourusername" with your actual username

### Step 4: Static Files
Add static files mapping:
- URL: `/static/`
- Directory: `/home/yourusername/minds-eye-photography/src/static/`

### Step 5: Test
1. Reload web app
2. Visit: https://yourusername.pythonanywhere.com
3. Admin: https://yourusername.pythonanywhere.com/admin
4. Password: mindseye2025

### Step 6: Custom Domain
1. Add custom domain in Web tab
2. Set up DNS records with your domain provider
3. SSL certificate will be generated automatically

## Features Included
- ✅ React website with 3:2 aspect ratio portfolio
- ✅ Modal gallery with navigation
- ✅ Admin interface for image management
- ✅ 13 wildlife images included
- ✅ Contact form functionality
- ✅ Mobile responsive design
- ✅ Image protection features

## Admin Interface
- Login: /admin
- Password: mindseye2025
- Upload images one at a time
- Add titles, descriptions, and categories
- Delete images with confirmation

## Directory Structure
```
minds-eye-photography/
├── src/
│   ├── main.py (Flask app)
│   ├── routes/
│   │   └── admin.py (Admin interface)
│   └── static/ (React website + images)
├── pythonanywhere_wsgi.py (WSGI config)
├── requirements.txt (Dependencies)
└── SETUP-INSTRUCTIONS.md (This file)
```

