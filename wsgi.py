"""
WSGI entry point for PythonAnywhere deployment
This file should be used in PythonAnywhere's WSGI configuration
"""
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/turktrendyshop'  # UPDATE THIS PATH
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'

# Import Flask app
from app import app as application

# This is what PythonAnywhere will use
if __name__ == "__main__":
    application.run()
