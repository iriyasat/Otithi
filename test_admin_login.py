#!/usr/bin/env python3
"""
Test script to verify admin login credentials
"""
import sys
import os
sys.path.append('/Applications/XAMPP/xamppfiles/htdocs/Othiti')

from app.models import User
from app.database import db

def test_admin_login():
    """Test admin login credentials"""
    print("Testing admin login credentials...")
    
    # Test admin credentials
    email = "admin@otithi.com"
    password = "admin123"
    
    print(f"Attempting to find user with email: {email}")
    user = User.get_by_email(email)
    
    if user:
        print(f"✓ User found: {user.full_name}")
        print(f"  - User ID: {user.id}")
        print(f"  - User Type: {user.user_type}")
        print(f"  - Email: {user.email}")
        print(f"  - Password hash exists: {bool(user.password_hash)}")
        print(f"  - Password hash length: {len(user.password_hash) if user.password_hash else 0}")
        
        # Test password
        print(f"\nTesting password '{password}'...")
        password_valid = user.check_password(password)
        print(f"Password validation result: {password_valid}")
        
        if password_valid:
            print("✅ Admin login credentials are WORKING!")
            return True
        else:
            print("❌ Admin password is INVALID!")
            return False
    else:
        print(f"❌ No user found with email: {email}")
        return False

if __name__ == "__main__":
    try:
        result = test_admin_login()
        print(f"\nFinal result: {'SUCCESS' if result else 'FAILED'}")
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
