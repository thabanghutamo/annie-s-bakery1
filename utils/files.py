"""File and directory utilities."""
from typing import Optional, Tuple
import os
from pathlib import Path
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import stat


# Upload directories configuration
UPLOAD_DIRS = {
    'products': 'static/uploads/products',
    'blog': 'static/uploads/blog',
    'orders': 'static/uploads/orders'
}


# Allowed file extensions
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}


def init_upload_dirs() -> None:
    """Create required upload directories if missing."""
    for dir_path in UPLOAD_DIRS.values():
        path = Path(dir_path)
        # Create directory if it doesn't exist
        path.mkdir(parents=True, exist_ok=True)
        # Set full permissions for the application
        try:
            if os.name == 'nt':  # Windows
                os.system(f'icacls "{path}" /grant:r "*S-1-1-0:(OI)(CI)F" /T')
            else:  # Unix/Linux
                path.chmod(0o777)
        except Exception as e:
            print(f"Warning: Could not set permissions on {path}: {e}")

def secure_upload_path(
    file: FileStorage,
    category: str
) -> Tuple[Optional[str], Optional[Path]]:
    """Generate a secure path for an uploaded file.
    
    Args:
        file: FileStorage object from request.files
        category: Key in UPLOAD_DIRS ('products', 'blog', 'orders')
    
    Returns:
        Tuple of (url_path, file_path) if valid, (None, None) if invalid
    """
    if not file or not file.filename:
        return None, None
        
    filename = secure_filename(file.filename)
    if not filename:
        return None, None
    
    # Check extension
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None, None
    
    # Add category prefix
    filename = f"{category}-{filename}"
    
    # Get directory for category
    dir_path = UPLOAD_DIRS.get(category)
    if not dir_path:
        return None, None
    
    # Build paths
    file_path = Path(dir_path) / filename
    url_path = '/static/uploads/' + category + '/' + filename
    
    return url_path, file_path


def save_uploaded_file(file: FileStorage, category: str) -> Optional[str]:
    """Save an uploaded file securely.
    
    Args:
        file: FileStorage object from request.files
        category: Key in UPLOAD_DIRS ('products', 'blog', 'orders')
    
    Returns:
        URL path to saved file or None if invalid/error
    """
    try:
        print(f"Processing upload: {file.filename} for category: {category}")
        url_path, file_path = secure_upload_path(file, category)
        if not url_path or not file_path:
            print(f"Invalid upload path for file: {file.filename}")
            return None
            
        print(f"Saving file to: {file_path} with URL: {url_path}")
        file.save(str(file_path))  # Convert Path to str for save()
        
        if not file_path.exists():
            print(f"File not saved successfully: {file_path}")
            return None
            
        print(f"File saved successfully: {file_path}")
        return url_path
        
    except Exception as e:
        print(f"Error saving file {file.filename}: {str(e)}")
        # Only try to clean up if file_path exists
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            print(f"Error cleaning up file {file_path}: {str(e)}")
        return None

def save_multiple_files(files: list[FileStorage], category: str) -> list[str]:
    """Save multiple uploaded files securely.
    
    Args:
        files: List of FileStorage objects from request.files
        category: Key in UPLOAD_DIRS ('products', 'blog', 'orders')
    
    Returns:
        List of URL paths to saved files. Invalid files are skipped.
    """
    saved_urls = []
    for file in files:
        if url := save_uploaded_file(file, category):
            saved_urls.append(url)
    return saved_urls
