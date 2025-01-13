import os
from datetime import datetime
import uuid

def generate_unique_filename(original_filename, prefix=''):
    """
    Generate a unique filename by combining:
    - Optional prefix
    - Original filename (without extension)
    - Current timestamp
    - Random UUID
    - Original extension
    """
    # Get the file extension
    name, ext = os.path.splitext(original_filename)
    
    # Generate timestamp string
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Generate a short UUID (first 8 characters)
    unique_id = str(uuid.uuid4())[:8]
    
    # Combine all parts with prefix if provided
    if prefix:
        new_filename = f"{prefix}_{name}_{timestamp}_{unique_id}{ext}"
    else:
        new_filename = f"{name}_{timestamp}_{unique_id}{ext}"
    
    return new_filename 