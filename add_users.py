#!/usr/bin/env python3
"""
Script to add new users to the Otithi database
"""
import mysql.connector
from werkzeug.security import generate_password_hash
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3307,  # XAMPP MySQL port
    'user': 'root',
    'password': '',  # Default XAMPP password is empty
    'database': 'otithi',
    'charset': 'utf8mb4'
}

def add_user(name, email, password, user_type, phone=None, bio=None):
    """Add a new user to the database"""
    try:
        # Connect to database
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            print(f"❌ User with email {email} already exists!")
            return False
        
        # Generate password hash
        password_hash = generate_password_hash(password)
        current_time = datetime.now()
        
        # Insert into users table
        user_query = """
            INSERT INTO users (name, email, password_hash) 
            VALUES (%s, %s, %s)
        """
        cursor.execute(user_query, (name, email, password_hash))
        user_id = cursor.lastrowid
        
        # Insert into user_details table
        details_query = """
            INSERT INTO user_details 
            (user_id, phone, bio, user_type, join_date, verified, is_active, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(details_query, (
            user_id, phone, bio, user_type, current_time, 
            True,  # verified = True
            True,  # is_active = True
            current_time, current_time
        ))
        
        # Commit the transaction
        connection.commit()
        print(f"✅ Successfully added user: {name} ({email}) as {user_type}")
        print(f"   User ID: {user_id}")
        return True
        
    except mysql.connector.Error as err:
        print(f"❌ Database error: {err}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def main():
    """Main function to add users"""
    print("🚀 Adding new users to Otithi database...")
    print("=" * 50)
    
    # Users to add
    users = [
        {
            'name': 'Ibrahim Hasan',
            'email': 'host@otithi.com',
            'password': 'password123',
            'user_type': 'host',
            'phone': '+8801712345678',
            'bio': 'Experienced host with multiple properties. Passionate about providing excellent guest experiences.'
        },
        {
            'name': 'Marzia Hossain',
            'email': 'guest@otithi.com',
            'password': 'password123',
            'user_type': 'guest',
            'phone': '+8801798765432',
            'bio': 'Travel enthusiast and frequent guest. Love exploring new places and meeting new people.'
        }
    ]
    
    success_count = 0
    for user in users:
        if add_user(**user):
            success_count += 1
        print()
    
    print("=" * 50)
    print(f"✅ Successfully added {success_count}/{len(users)} users")
    
    if success_count > 0:
        print("\n📋 Login Credentials:")
        print("-" * 30)
        for user in users[:success_count]:
            print(f"👤 {user['name']} ({user['user_type'].title()})")
            print(f"   Email: {user['email']}")
            print(f"   Password: {user['password']}")
            print()

if __name__ == "__main__":
    main()
