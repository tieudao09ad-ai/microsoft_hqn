import sys
import os

# Add application directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask application object
from app import app as application
