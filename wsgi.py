"""
WSGI entry point for the application
"""
import os
import sys

# Add the current directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import the Flask app
from src.main import app

# This allows gunicorn to find the app
if __name__ == "__main__":
    app.run()

