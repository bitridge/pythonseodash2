import os
import sys

# Add your project directory to the sys.path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Set environment variable for Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seo_work_log.settings_prod')

# Create temp directory for uploads if it doesn't exist
temp_upload_dir = os.path.join(project_dir, 'tmp')
if not os.path.exists(temp_upload_dir):
    os.makedirs(temp_upload_dir)

# Create logs directory if it doesn't exist
logs_dir = os.path.join(project_dir, 'logs')
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Create media and static directories
media_dir = os.path.join(project_dir, 'mediafiles')
static_dir = os.path.join(project_dir, 'staticfiles')
if not os.path.exists(media_dir):
    os.makedirs(media_dir)
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# Set up logging
import logging
logging.basicConfig(
    filename=os.path.join(logs_dir, 'application.log'),
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(message)s'
)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application() 