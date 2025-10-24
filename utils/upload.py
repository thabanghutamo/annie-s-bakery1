"""File upload utilities and security."""
import os
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import current_app
import stat

UPLOAD_DIRS = {
    'products': 'static/uploads/products',
    'blog': 'static/uploads/blog',
    'orders': 'static/uploads/orders'
}

def init_upload_dirs():
    """Create required upload directories if missing."""
    for dir_path in UPLOAD_DIRS.values():
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        # Ensure directory is writable
        path.chmod(path.stat().st_mode | stat.S_IWRITE)

def allowed_file(filename):
    """Check if uploaded file has an allowed extension."""
    if '.' not in filename:
        return False
    ext = os.path.splitext(filename)[1].lower()
    return ext in current_app.config['UPLOAD_EXTENSIONS']

def save_upload(file, category):
    """Save an uploaded file securely.
    
    Args:
        file: FileStorage object from request.files
        category: Key in UPLOAD_DIRS ('products', 'blog', 'orders')
        
    Returns:
        URL path to the saved file relative to static dir, or None if invalid
    """
    if not file or not file.filename or not allowed_file(file.filename):
        return None
        
    filename = secure_filename(file.filename)
    if not filename:
        return None
        
    # Add category prefix to filename for organization
    filename = f"{category}-{filename}"
    
    upload_path = Path(UPLOAD_DIRS[category]) / filename
    try:
        file.save(upload_path)
        # Convert Windows path to URL format
        url_path = '/' + str(upload_path).replace('\\', '/')
        return url_path
    except Exception:
        return None