#!/usr/bin/env python3
"""
Create Admin User Script for Otithi
This script creates an admin user in the database
"""

import mysql.connector
from mysql.connector import Error
import sys
import os
from werkzeug.security import generate_password_hash

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

def create_admin_user():
    """Create an admin user"""
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE,
            autocommit=True
        )
        
        print("✅ Connected to database")
        
        # Get admin details from user input
        print("\n📝 Enter admin user details:")
        name = input("Full Name (default: Admin User): ").strip() or "Admin User"
        email = input("Email (default: admin@otithi.com): ").strip() or "admin@otithi.com"
        password = input("Password (default: admin123): ").strip() or "admin123"
        
        # Check if user already exists
        cursor = connection.cursor()
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            # Update existing user to admin
            cursor.execute("UPDATE users SET user_type = 'admin' WHERE email = %s", (email,))
            print(f"✅ Updated existing user {email} to admin")
        else:
            # Create new admin user
            password_hash = generate_password_hash(password)
            insert_query = """
                INSERT INTO users (name, email, password_hash, user_type, join_date)
                VALUES (%s, %s, %s, 'admin', NOW())
            """
            cursor.execute(insert_query, (name, email, password_hash))
            print(f"✅ Created new admin user: {email}")
        
        cursor.close()
        connection.close()
        
        print(f"\n🎉 Admin user ready!")
        print(f"📧 Email: {email}")
        print(f"🔑 Password: {password}")
        print(f"👤 Name: {name}")
        print("\n🚀 You can now login as admin!")
        
        return True
        
    except Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔐 Otithi Admin User Creator")
    print("=" * 30)
    
    success = create_admin_user()
    sys.exit(0 if success else 1)
