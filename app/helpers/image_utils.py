"""
Image utility functions for handling file uploads, resizing, and compression.
"""

import os
import uuid
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename

def save_image(uploaded_file, folder='uploads', resize_to=None, max_size=(800, 600)):
    """
    Save an uploaded image file with optional resizing.
    
    Args:
        uploaded_file: FileStorage object from Flask
        folder: Subfolder within upload directory
        resize_to: Tuple of (width, height) for resizing
        max_size: Maximum dimensions if resize_to is None
    
    Returns:
        str: Filename of saved image
    """
    if not uploaded_file or uploaded_file.filename == '':
        return None
    
    # Generate unique filename
    original_filename = secure_filename(uploaded_file.filename)
    file_ext = os.path.splitext(original_filename)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    
    # Create folder path
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'app/static/uploads')
    folder_path = os.path.join(upload_folder, folder)
    os.makedirs(folder_path, exist_ok=True)
    
    # Save file
    filepath = os.path.join(folder_path, unique_filename)
    uploaded_file.save(filepath)
    
    # Resize if needed
    if resize_to:
        resize_image(filepath, resize_to)
    elif max_size:
        resize_image(filepath, max_size)
    
    return unique_filename

def delete_image(filename, folder='uploads'):
    """
    Delete an image file from the upload directory.
    
    Args:
        filename: Name of the file to delete
        folder: Subfolder within upload directory
    """
    if not filename:
        return
    
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'app/static/uploads')
    filepath = os.path.join(upload_folder, folder, filename)
    
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    except Exception as e:
        current_app.logger.error(f"Error deleting image {filepath}: {e}")
        return False

def resize_image(filepath, size):
    """
    Resize an image to specified dimensions while maintaining aspect ratio.
    
    Args:
        filepath: Path to the image file
        size: Tuple of (width, height) for target size
    """
    try:
        with Image.open(filepath) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize while maintaining aspect ratio
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(filepath, quality=85, optimize=True)
    except Exception as e:
        current_app.logger.error(f"Error resizing image {filepath}: {e}")

def compress_image(filepath, quality=70):
    """
    Compress an image to reduce file size.
    
    Args:
        filepath: Path to the image file
        quality: JPEG quality (1-100, higher is better quality)
    """
    try:
        with Image.open(filepath) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            img.save(filepath, quality=quality, optimize=True)
    except Exception as e:
        current_app.logger.error(f"Error compressing image {filepath}: {e}")

def get_image_info(filepath):
    """
    Get basic information about an image file.
    
    Args:
        filepath: Path to the image file
    
    Returns:
        dict: Image information (width, height, format, size)
    """
    try:
        with Image.open(filepath) as img:
            file_size = os.path.getsize(filepath)
            return {
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
                'size_bytes': file_size,
                'size_mb': round(file_size / (1024 * 1024), 2)
            }
    except Exception as e:
        current_app.logger.error(f"Error getting image info for {filepath}: {e}")
        return None

def is_valid_image(filename):
    """
    Check if a filename has a valid image extension.
    
    Args:
        filename: Name of the file to check
    
    Returns:
        bool: True if valid image extension
    """
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    return os.path.splitext(filename.lower())[1] in allowed_extensions

def get_file_size_mb(filepath):
    """
    Get file size in megabytes.
    
    Args:
        filepath: Path to the file
    
    Returns:
        float: File size in MB
    """
    try:
        size_bytes = os.path.getsize(filepath)
        return round(size_bytes / (1024 * 1024), 2)
    except Exception:
        return 0 