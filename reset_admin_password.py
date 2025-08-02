#!/usr/bin/env python3
"""
Reset Admin Password Script
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models import User
from werkzeug.security import generate_password_hash

def reset_admin_password():
    """Reset admin password"""
    print("Resetting admin password...")
    
    try:
        # Find admin user
        admin_user = User.get_by_email('admin@otithi.com')
        if not admin_user:
            print("❌ Admin user not found")
            return False
        
        # Generate new password hash
        new_password = "admin123"
        new_hash = generate_password_hash(new_password)
        
        print(f"Admin user ID: {admin_user.id}")
        print(f"Current hash: {admin_user.password_hash[:50]}...")
        print(f"New hash: {new_hash[:50]}...")
        
        # Update password in database
        from app.database import Database
        db = Database()
        
        query = "UPDATE users SET password_hash = %s WHERE user_id = %s"
        success = db.execute_update(query, (new_hash, admin_user.id))
        
        if success:
            print("✅ Password updated in database")
            
            # Test the new password
            updated_user = User.get_by_email('admin@otithi.com')
            if updated_user and updated_user.check_password(new_password):
                print("✅ New password verified successfully")
                return True
            else:
                print("❌ New password verification failed")
                return False
        else:
            print("❌ Failed to update password")
            return False
            
    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Admin Password Reset ===\n")
    
    if reset_admin_password():
        print("\n✅ Admin password reset complete!")
        print("Email: admin@otithi.com")
        print("Password: admin123")
    else:
        print("\n❌ Admin password reset failed")
