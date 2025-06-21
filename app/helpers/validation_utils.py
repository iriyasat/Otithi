"""
Validation utility functions for form and data validation.
"""

import re
from datetime import datetime, date
from typing import Any, Dict, List, Optional

def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate phone number format (Bangladesh)."""
    if not phone:
        return False
    
    # Remove spaces, dashes, and parentheses
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Bangladesh phone number patterns
    patterns = [
        r'^(\+880|880)?1[3-9]\d{8}$',  # Mobile numbers
        r'^(\+880|880)?2\d{7,8}$',     # Landline numbers
    ]
    
    return any(re.match(pattern, phone) for pattern in patterns)

def validate_nid(nid: str) -> bool:
    """Validate National ID format (Bangladesh)."""
    if not nid:
        return False
    
    # Remove spaces and dashes
    nid = re.sub(r'[\s\-]', '', nid)
    
    # NID should be 10 or 13 digits
    if len(nid) not in [10, 13]:
        return False
    
    return nid.isdigit()

def validate_password(password: str) -> Dict[str, Any]:
    """Validate password strength."""
    result = {
        'valid': True,
        'errors': [],
        'strength': 'weak'
    }
    
    if len(password) < 8:
        result['errors'].append('Password must be at least 8 characters long')
        result['valid'] = False
    
    if not re.search(r'[A-Z]', password):
        result['errors'].append('Password must contain at least one uppercase letter')
        result['valid'] = False
    
    if not re.search(r'[a-z]', password):
        result['errors'].append('Password must contain at least one lowercase letter')
        result['valid'] = False
    
    if not re.search(r'\d', password):
        result['errors'].append('Password must contain at least one number')
        result['valid'] = False
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        result['errors'].append('Password must contain at least one special character')
        result['valid'] = False
    
    # Calculate strength
    if result['valid']:
        if len(password) >= 12:
            result['strength'] = 'strong'
        elif len(password) >= 10:
            result['strength'] = 'medium'
        else:
            result['strength'] = 'weak'
    
    return result

def validate_date_range(start_date: str, end_date: str) -> Dict[str, Any]:
    """Validate date range."""
    result = {
        'valid': True,
        'errors': [],
        'start_date': None,
        'end_date': None
    }
    
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        result['start_date'] = start
        result['end_date'] = end
        
        if start < date.today():
            result['errors'].append('Start date cannot be in the past')
            result['valid'] = False
        
        if end <= start:
            result['errors'].append('End date must be after start date')
            result['valid'] = False
        
        if (end - start).days > 30:
            result['errors'].append('Booking period cannot exceed 30 days')
            result['valid'] = False
            
    except ValueError:
        result['errors'].append('Invalid date format. Use YYYY-MM-DD')
        result['valid'] = False
    
    return result

def validate_price(price: str) -> bool:
    """Validate price format."""
    if not price:
        return False
    
    try:
        price_float = float(price)
        return price_float > 0
    except ValueError:
        return False

def validate_listing_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate listing form data."""
    result = {
        'valid': True,
        'errors': []
    }
    
    required_fields = ['title', 'description', 'price', 'location']
    
    for field in required_fields:
        if not data.get(field):
            result['errors'].append(f'{field.title()} is required')
            result['valid'] = False
    
    if data.get('title') and len(data['title']) < 10:
        result['errors'].append('Title must be at least 10 characters long')
        result['valid'] = False
    
    if data.get('description') and len(data['description']) < 50:
        result['errors'].append('Description must be at least 50 characters long')
        result['valid'] = False
    
    if data.get('price') and not validate_price(str(data['price'])):
        result['errors'].append('Invalid price format')
        result['valid'] = False
    
    return result

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS."""
    if not text:
        return ''
    
    # Remove potentially dangerous HTML tags
    dangerous_tags = ['script', 'iframe', 'object', 'embed', 'form']
    for tag in dangerous_tags:
        text = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(f'<{tag}[^>]*/>', '', text, flags=re.IGNORECASE)
    
    # Remove JavaScript events
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    
    return text.strip()

def validate_file_upload(filename: str, allowed_extensions: List[str], max_size_mb: int = 5) -> Dict[str, Any]:
    """Validate file upload."""
    result = {
        'valid': True,
        'errors': []
    }
    
    if not filename:
        result['errors'].append('No file selected')
        result['valid'] = False
        return result
    
    # Check file extension
    file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
    if file_ext not in allowed_extensions:
        result['errors'].append(f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}')
        result['valid'] = False
    
    return result 