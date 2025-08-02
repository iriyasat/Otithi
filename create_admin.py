#!/usr/bin/env python3
"""
Create Admin User Script
Run this to create an admin user for testing
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models import User
from werkzeug.security import generate_password_hash

def create_admin_user():
    """Create an admin user"""
    print("Creating admin user...")
    
    try:
        # Check if admin user already exists
        existing_admin = User.get_by_email('admin@otithi.com')
        if existing_admin:
            print("Admin user already exists!")
            print(f"Email: {existing_admin.email}")
            print(f"User Type: {existing_admin.user_type}")
            print(f"Verified: {existing_admin.verified}")
            return existing_admin
        
        # Create new admin user
        admin_user = User.create(
            full_name="Administrator",
            email="admin@otithi.com",
            password="admin123",  # Simple password for testing
            phone="+8801234567890",
            bio="System Administrator",
            user_type="admin"
        )
        
        if admin_user:
            print("✅ Admin user created successfully!")
            print(f"Email: admin@otithi.com")
            print(f"Password: admin123")
            print(f"User Type: admin")
            
            # Verify the user
            if hasattr(admin_user, 'update_verification_status'):
                admin_user.update_verification_status(True)
                print("✅ Admin user verified!")
            
            return admin_user
        else:
            print("❌ Failed to create admin user")
            return None
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return None

def test_admin_login():
    """Test admin login"""
    print("\nTesting admin login...")
    
    try:
        admin_user = User.get_by_email('admin@otithi.com')
        if not admin_user:
            print("❌ Admin user not found")
            return False
        
        print(f"✅ Admin user found: {admin_user.full_name}")
        print(f"User Type: {admin_user.user_type}")
        print(f"Email: {admin_user.email}")
        
        # Test password check
        test_password = "admin123"
        if admin_user.check_password(test_password):
            print("✅ Password check successful")
            return True
        else:
            print("❌ Password check failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing admin login: {e}")
        return False

if __name__ == "__main__":
    print("=== Otithi Admin User Setup ===\n")
    
    # Create admin user
    admin_user = create_admin_user()
    
    if admin_user:
        # Test login
        success = test_admin_login()
        
        if success:
            print("\n✅ Admin setup complete! You can now login with:")
            print("Email: admin@otithi.com")
            print("Password: admin123")
        else:
            print("\n❌ Admin setup failed during testing")
    else:
        print("\n❌ Admin setup failed")
