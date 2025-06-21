"""
Utility functions for Otithi Platform
Common helper functions used across the application.
"""

from datetime import date, datetime, timedelta
from typing import List, Tuple, Optional
from sqlalchemy import and_, or_
from .models import Booking, BookingStatus, Listing, ListingStatus, AuditLog
from . import db
from functools import wraps
from flask import current_app, request
from sqlalchemy.exc import SQLAlchemyError
import logging
import os
import uuid
from PIL import Image

logger = logging.getLogger(__name__)

def transactional(func):
    """
    Decorator to handle database transactions for write operations.
    Use this for routes that modify data.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Set session to read-write mode for write operations
            db.session.execute('SET SESSION TRANSACTION READ WRITE')
            
            # Execute the function
            result = func(*args, **kwargs)
            
            # Commit the transaction
            db.session.commit()
            return result
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error in {func.__name__}: {str(e)}")
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise
        finally:
            # Reset to read-only mode
            db.session.execute('SET SESSION TRANSACTION READ ONLY')
    
    return wrapper

def read_only(func):
    """
    Decorator to explicitly mark read-only operations.
    This ensures the session stays in read-only mode.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Ensure read-only mode
            db.session.execute('SET SESSION TRANSACTION READ ONLY')
            return func(*args, **kwargs)
        except SQLAlchemyError as e:
            logger.error(f"Database error in read-only operation {func.__name__}: {str(e)}")
            raise
    
    return wrapper

def with_transaction():
    """
    Context manager for explicit transaction control.
    Use this when you need fine-grained control over transactions.
    """
    class TransactionContext:
        def __enter__(self):
            db.session.execute('SET SESSION TRANSACTION READ WRITE')
            return db.session
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            try:
                if exc_type is not None:
                    db.session.rollback()
                    logger.error(f"Transaction rolled back due to: {exc_val}")
                else:
                    db.session.commit()
            finally:
                db.session.execute('SET SESSION TRANSACTION READ ONLY')
    
    return TransactionContext()

def safe_commit():
    """
    Safely commit the current transaction with error handling.
    """
    try:
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Commit failed: {str(e)}")
        return False

def safe_rollback():
    """
    Safely rollback the current transaction.
    """
    try:
        db.session.rollback()
        return True
    except SQLAlchemyError as e:
        logger.error(f"Rollback failed: {str(e)}")
        return False

def check_booking_availability(listing_id: str, check_in: date, check_out: date, 
                              exclude_booking_id: Optional[str] = None) -> bool:
    """
    Check if a listing is available for the given date range.
    
    Args:
        listing_id: ID of the listing to check
        check_in: Check-in date
        check_out: Check-out date
        exclude_booking_id: Booking ID to exclude from the check (for updates)
    
    Returns:
        bool: True if available, False if conflicting bookings exist
    """
    try:
        # Query for overlapping bookings
        query = Booking.query.filter(
            and_(
                Booking.listing_id == listing_id,
                Booking.status.in_([
                    BookingStatus.PENDING, 
                    BookingStatus.CONFIRMED, 
                    BookingStatus.CHECKED_IN
                ]),
                or_(
                    # New booking starts before existing booking ends AND
                    # New booking ends after existing booking starts
                    and_(
                        check_in < Booking.check_out_date,
                        check_out > Booking.check_in_date
                    )
                )
            )
        )
        
        # Exclude specific booking (for updates)
        if exclude_booking_id:
            query = query.filter(Booking.id != exclude_booking_id)
        
        conflicting_bookings = query.count()
        return conflicting_bookings == 0
        
    except Exception as e:
        # Log error and assume conflict for safety
        print(f"Error checking booking availability: {e}")
        return False


def get_available_dates(listing_id: str, start_date: date, end_date: date, 
                       max_days: int = 30) -> List[Tuple[date, date]]:
    """
    Get available date ranges for a listing within a given period.
    
    Args:
        listing_id: ID of the listing
        start_date: Start of search period
        end_date: End of search period
        max_days: Maximum length of stay to consider
    
    Returns:
        List of (start_date, end_date) tuples for available periods
    """
    try:
        # Get all conflicting bookings
        conflicting_bookings = Booking.query.filter(
            and_(
                Booking.listing_id == listing_id,
                Booking.status.in_([
                    BookingStatus.PENDING, 
                    BookingStatus.CONFIRMED, 
                    BookingStatus.CHECKED_IN
                ]),
                or_(
                    Booking.check_in_date <= end_date,
                    Booking.check_out_date >= start_date
                )
            )
        ).order_by(Booking.check_in_date).all()
        
        available_periods = []
        current_date = start_date
        
        for booking in conflicting_bookings:
            # If there's a gap before this booking
            if current_date < booking.check_in_date:
                gap_start = current_date
                gap_end = booking.check_in_date
                
                # Add available periods within this gap
                while gap_start < gap_end:
                    period_end = min(gap_start + timedelta(days=max_days), gap_end)
                    if period_end > gap_start:
                        available_periods.append((gap_start, period_end))
                    gap_start = period_end
            
            # Move current date to after this booking
            current_date = max(current_date, booking.check_out_date)
        
        # Check if there's availability after the last booking
        if current_date < end_date:
            while current_date < end_date:
                period_end = min(current_date + timedelta(days=max_days), end_date)
                if period_end > current_date:
                    available_periods.append((current_date, period_end))
                current_date = period_end
        
        return available_periods
        
    except Exception as e:
        print(f"Error getting available dates: {e}")
        return []


def calculate_booking_price(listing_id: str, check_in: date, check_out: date, 
                           guest_count: int = 1) -> float:
    """
    Calculate the total price for a booking.
    
    Args:
        listing_id: ID of the listing
        check_in: Check-in date
        check_out: Check-out date
        guest_count: Number of guests
    
    Returns:
        float: Total price for the booking
    """
    try:
        listing = Listing.query.get(listing_id)
        if not listing:
            return 0.0
        
        # Calculate number of nights
        nights = (check_out - check_in).days
        if nights <= 0:
            return 0.0
        
        # Calculate base price
        base_price = float(listing.price_per_night) * nights
        
        # Apply guest count multiplier (if more than capacity)
        if guest_count > listing.guest_capacity:
            # Add 20% per additional guest
            extra_guests = guest_count - listing.guest_capacity
            extra_charge = base_price * 0.2 * extra_guests
            base_price += extra_charge
        
        return round(base_price, 2)
        
    except Exception as e:
        print(f"Error calculating booking price: {e}")
        return 0.0


def validate_booking_dates(check_in: date, check_out: date, 
                          min_stay: int = 1, max_stay: int = 30) -> Tuple[bool, str]:
    """
    Validate booking dates.
    
    Args:
        check_in: Check-in date
        check_out: Check-out date
        min_stay: Minimum stay in nights
        max_stay: Maximum stay in nights
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    today = date.today()
    
    # Check if dates are in the past
    if check_in < today:
        return False, "Check-in date cannot be in the past"
    
    if check_out < today:
        return False, "Check-out date cannot be in the past"
    
    # Check if check-out is after check-in
    if check_out <= check_in:
        return False, "Check-out date must be after check-in date"
    
    # Check minimum stay
    nights = (check_out - check_in).days
    if nights < min_stay:
        return False, f"Minimum stay is {min_stay} night(s)"
    
    # Check maximum stay
    if nights > max_stay:
        return False, f"Maximum stay is {max_stay} night(s)"
    
    return True, ""


def format_address(city: str = None, district: str = None, 
                  region: str = None, location: str = None) -> str:
    """
    Format a complete address from components.
    
    Args:
        city: City name
        district: District name
        region: Region name
        location: Full location string
    
    Returns:
        str: Formatted address
    """
    parts = []
    
    if city:
        parts.append(city)
    if district:
        parts.append(district)
    if region:
        parts.append(region)
    if location:
        parts.append(location)
    
    return ', '.join(parts) if parts else "Location not specified"


def get_bangladesh_districts() -> List[str]:
    """
    Get list of Bangladesh districts for dropdown options.
    
    Returns:
        List of district names
    """
    return [
        "Dhaka", "Chittagong", "Rajshahi", "Khulna", "Barisal", "Sylhet", 
        "Rangpur", "Mymensingh", "Comilla", "Noakhali", "Feni", "Chandpur",
        "Lakshmipur", "Cox's Bazar", "Brahmanbaria", "Narayanganj", "Tangail",
        "Gazipur", "Narsingdi", "Kishoreganj", "Netrokona", "Jamalpur", 
        "Sherpur", "Moulvibazar", "Habiganj", "Sunamganj", "Bogra", "Joypurhat",
        "Naogaon", "Natore", "Chapainawabganj", "Pabna", "Sirajganj", 
        "Kushtia", "Meherpur", "Jhenaidah", "Magura", "Narail", "Jessore",
        "Satkhira", "Bagerhat", "Pirojpur", "Jhalokati", "Patuakhali", 
        "Bhola", "Barguna", "Panchagarh", "Thakurgaon", "Dinajpur", 
        "Nilphamari", "Lalmonirhat", "Kurigram", "Gaibandha"
    ]


def get_bangladesh_cities() -> List[str]:
    """
    Get list of major Bangladesh cities for dropdown options.
    
    Returns:
        List of city names
    """
    return [
        "Dhaka", "Chittagong", "Rajshahi", "Khulna", "Barisal", "Sylhet",
        "Rangpur", "Mymensingh", "Comilla", "Narayanganj", "Gazipur",
        "Tangail", "Bogra", "Kushtia", "Jessore", "Cox's Bazar",
        "Brahmanbaria", "Noakhali", "Feni", "Chandpur", "Lakshmipur",
        "Narsingdi", "Kishoreganj", "Netrokona", "Jamalpur", "Sherpur",
        "Moulvibazar", "Habiganj", "Sunamganj", "Joypurhat", "Naogaon",
        "Natore", "Chapainawabganj", "Pabna", "Sirajganj", "Meherpur",
        "Jhenaidah", "Magura", "Narail", "Satkhira", "Bagerhat",
        "Pirojpur", "Jhalokati", "Patuakhali", "Bhola", "Barguna"
    ]


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename for safe storage.
    
    Args:
        filename: Original filename
    
    Returns:
        str: Sanitized filename
    """
    import re
    import unicodedata
    
    # Remove accents and normalize
    filename = unicodedata.normalize('NFKD', filename)
    
    # Remove special characters except dots and hyphens
    filename = re.sub(r'[^\w\-_.]', '_', filename)
    
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    
    # Remove leading/trailing underscores
    filename = filename.strip('_')
    
    return filename


def generate_unique_filename(original_filename: str, prefix: str = "") -> str:
    """
    Generate a unique filename with timestamp.
    
    Args:
        original_filename: Original filename
        prefix: Optional prefix for the filename
    
    Returns:
        str: Unique filename
    """
    import time
    import os
    
    # Get file extension
    name, ext = os.path.splitext(original_filename)
    
    # Sanitize the name
    sanitized_name = sanitize_filename(name)
    
    # Add timestamp for uniqueness
    timestamp = int(time.time())
    
    # Combine parts
    if prefix:
        unique_filename = f"{prefix}_{sanitized_name}_{timestamp}{ext}"
    else:
        unique_filename = f"{sanitized_name}_{timestamp}{ext}"
    
    return unique_filename.lower()


def format_currency(amount: float, currency: str = "BDT") -> str:
    """
    Format currency for display.
    
    Args:
        amount: Amount to format
        currency: Currency code
    
    Returns:
        str: Formatted currency string
    """
    if currency == "BDT":
        return f"৳{amount:,.2f}"
    else:
        return f"{currency} {amount:,.2f}"


def format_date_range(start_date: date, end_date: date) -> str:
    """
    Format a date range for display.
    
    Args:
        start_date: Start date
        end_date: End date
    
    Returns:
        str: Formatted date range
    """
    if start_date == end_date:
        return start_date.strftime("%B %d, %Y")
    else:
        return f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"


def get_booking_status_color(status: BookingStatus) -> str:
    """
    Get Bootstrap color class for booking status.
    
    Args:
        status: Booking status
    
    Returns:
        str: Bootstrap color class
    """
    status_colors = {
        BookingStatus.PENDING: "warning",
        BookingStatus.CONFIRMED: "info",
        BookingStatus.CHECKED_IN: "primary",
        BookingStatus.CHECKED_OUT: "success",
        BookingStatus.CANCELLED: "danger"
    }
    return status_colors.get(status, "secondary")


def get_listing_status_color(status: ListingStatus) -> str:
    """
    Get Bootstrap color class for listing status.
    
    Args:
        status: Listing status
    
    Returns:
        str: Bootstrap color class
    """
    status_colors = {
        ListingStatus.DRAFT: "secondary",
        ListingStatus.PENDING: "warning",
        ListingStatus.APPROVED: "success",
        ListingStatus.REJECTED: "danger",
        ListingStatus.INACTIVE: "dark"
    }
    return status_colors.get(status, "secondary")


def log_audit_event(action, resource_type, resource_id=None, user_id=None, 
                   details=None, ip_address=None, user_agent=None):
    """
    Comprehensive audit logging utility
    
    Args:
        action (str): The action performed (e.g., 'login', 'listing_created', 'booking_cancelled')
        resource_type (str): Type of resource affected (e.g., 'user', 'listing', 'booking')
        resource_id: ID of the affected resource
        user_id: ID of the user performing the action
        details (str): Additional details about the action
        ip_address (str): IP address of the user
        user_agent (str): User agent string
    """
    try:
        # Get request context if available
        if not ip_address and request:
            ip_address = request.remote_addr
        if not user_agent and request:
            user_agent = request.headers.get('User-Agent', '')
        
        # Create audit log entry
        log = AuditLog.log_event(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Commit immediately for critical events
        if action in ['login_failed', 'admin_action', 'payment_processed', 'security_violation']:
            db.session.commit()
        
        return log
    except Exception as e:
        current_app.logger.error(f"Failed to log audit event: {e}")
        return None

def log_security_event(action, user_id=None, details=None, severity='info'):
    """
    Log security-related events
    
    Args:
        action (str): Security action (e.g., 'login_attempt', 'permission_denied', 'suspicious_activity')
        user_id: ID of the user involved
        details (str): Details about the security event
        severity (str): Severity level ('info', 'warning', 'error', 'critical')
    """
    details_with_severity = f"[{severity.upper()}] {details}" if details else f"[{severity.upper()}] {action}"
    
    return log_audit_event(
        action=f"security_{action}",
        resource_type='security',
        user_id=user_id,
        details=details_with_severity,
        ip_address=request.remote_addr if request else None,
        user_agent=request.headers.get('User-Agent', '') if request else None
    )

def log_user_activity(user, action, details=None):
    """
    Log user activity with automatic context
    
    Args:
        user: User object performing the action
        action (str): Action being performed
        details (str): Additional details
    """
    return log_audit_event(
        action=action,
        resource_type='user',
        resource_id=user.id,
        user_id=user.id,
        details=details,
        ip_address=request.remote_addr if request else None,
        user_agent=request.headers.get('User-Agent', '') if request else None
    )

def log_admin_action(admin_user, action, target_type, target_id, details=None):
    """
    Log admin actions with enhanced security tracking
    
    Args:
        admin_user: Admin user performing the action
        action (str): Admin action performed
        target_type (str): Type of target affected
        target_id: ID of the target
        details (str): Additional details
    """
    return log_audit_event(
        action=f"admin_{action}",
        resource_type=target_type,
        resource_id=target_id,
        user_id=admin_user.id,
        details=f"Admin {admin_user.username}: {details}" if details else f"Admin {admin_user.username} performed {action}",
        ip_address=request.remote_addr if request else None,
        user_agent=request.headers.get('User-Agent', '') if request else None
    )

def get_audit_summary(days=30, user_id=None, action_type=None):
    """
    Get audit log summary for reporting
    
    Args:
        days (int): Number of days to look back
        user_id: Filter by specific user
        action_type (str): Filter by action type
    
    Returns:
        dict: Summary statistics
    """
    from datetime import timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    query = AuditLog.query.filter(AuditLog.timestamp >= cutoff_date)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if action_type:
        query = query.filter(AuditLog.action.like(f"%{action_type}%"))
    
    logs = query.all()
    
    summary = {
        'total_events': len(logs),
        'unique_users': len(set(log.user_id for log in logs if log.user_id)),
        'actions': {},
        'resource_types': {},
        'daily_activity': {}
    }
    
    for log in logs:
        # Count actions
        summary['actions'][log.action] = summary['actions'].get(log.action, 0) + 1
        
        # Count resource types
        summary['resource_types'][log.resource_type] = summary['resource_types'].get(log.resource_type, 0) + 1
        
        # Count daily activity
        date_str = log.timestamp.strftime('%Y-%m-%d')
        summary['daily_activity'][date_str] = summary['daily_activity'].get(date_str, 0) + 1
    
    return summary 