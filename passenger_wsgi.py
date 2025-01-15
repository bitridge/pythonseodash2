import os
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'seo_dashboard.settings'

# Create the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application() 