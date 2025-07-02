#!/usr/bin/env python3
"""
Automated Database Upgrade Script for Otithi
This script automatically applies database schema updates
"""

import mysql.connector
from mysql.connector import Error
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

def connect_to_database():
    """Connect to the MySQL database"""
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE,
            autocommit=True
        )
        if connection.is_connected():
            print(f"✅ Successfully connected to MySQL database '{Config.MYSQL_DATABASE}'")
            return connection
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        return None

def execute_upgrade(connection, upgrade_sql, description):
    """Execute a database upgrade"""
    try:
        cursor = connection.cursor()
        print(f"🔄 Applying upgrade: {description}")
        
        # Split multiple statements and execute them one by one
        statements = [stmt.strip() for stmt in upgrade_sql.split(';') if stmt.strip()]
        
        for statement in statements:
            if statement:
                cursor.execute(statement)
                print(f"   ✅ Executed: {statement[:50]}...")
        
        cursor.close()
        print(f"✅ Successfully applied: {description}")
        return True
        
    except Error as e:
        print(f"❌ Error applying upgrade '{description}': {e}")
        return False

def check_admin_user_type_exists(connection):
    """Check if admin user type already exists"""
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW COLUMNS FROM users LIKE 'user_type'")
        result = cursor.fetchone()
        cursor.close()
        
        if result:
            column_type = result[1]  # Type column
            return 'admin' in column_type
        return False
    except Error as e:
        print(f"❌ Error checking user_type column: {e}")
        return False

def create_admin_user(connection, email="admin@otithi.com", password="admin123", name="Admin User"):
    """Create a default admin user if none exists"""
    try:
        from werkzeug.security import generate_password_hash
        cursor = connection.cursor()
        
        # Check if admin user already exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE user_type = 'admin'")
        admin_count = cursor.fetchone()[0]
        
        if admin_count > 0:
            print("✅ Admin user already exists")
            cursor.close()
            return True
        
        # Create admin user
        password_hash = generate_password_hash(password)
        insert_query = """
            INSERT INTO users (name, email, password_hash, user_type, join_date)
            VALUES (%s, %s, %s, 'admin', NOW())
        """
        
        cursor.execute(insert_query, (name, email, password_hash))
        admin_id = cursor.lastrowid
        cursor.close()
        
        print(f"✅ Created admin user:")
        print(f"   📧 Email: {email}")
        print(f"   🔑 Password: {password}")
        print(f"   🆔 User ID: {admin_id}")
        print("   ⚠️  Please change the password after first login!")
        
        return True
        
    except Error as e:
        print(f"❌ Error creating admin user: {e}")
        return False

def add_missing_columns(connection):
    """Add any missing columns to existing tables"""
    upgrades = [
        {
            'sql': "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)",
            'description': "Add password_hash column to users table"
        },
        {
            'sql': "ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT",
            'description': "Add bio column to users table"
        },
        {
            'sql': "ALTER TABLE users ADD COLUMN IF NOT EXISTS verified BOOLEAN DEFAULT FALSE",
            'description': "Add verified column to users table"
        },
        {
            'sql': "ALTER TABLE listings ADD COLUMN IF NOT EXISTS rating DECIMAL(2,1) DEFAULT 0.0",
            'description': "Add rating column to listings table"
        },
        {
            'sql': "ALTER TABLE listings ADD COLUMN IF NOT EXISTS reviews_count INT DEFAULT 0",
            'description': "Add reviews_count column to listings table"
        }
    ]
    
    success_count = 0
    for upgrade in upgrades:
        if execute_upgrade(connection, upgrade['sql'], upgrade['description']):
            success_count += 1
    
    return success_count == len(upgrades)

def main():
    """Main upgrade function"""
    print("🚀 Starting Otithi Database Upgrade...")
    print("=" * 50)
    
    # Connect to database
    connection = connect_to_database()
    if not connection:
        print("❌ Cannot proceed without database connection")
        return False
    
    try:
        upgrade_success = True
        
        # 1. Update user_type ENUM to include admin
        if not check_admin_user_type_exists(connection):
            admin_enum_sql = "ALTER TABLE users MODIFY COLUMN user_type ENUM('guest', 'host', 'admin') DEFAULT 'guest'"
            if not execute_upgrade(connection, admin_enum_sql, "Add 'admin' to user_type ENUM"):
                upgrade_success = False
        else:
            print("✅ Admin user type already exists in database")
        
        # 2. Add missing columns
        if not add_missing_columns(connection):
            upgrade_success = False
        
        # 3. Create default admin user
        if not create_admin_user(connection):
            upgrade_success = False
        
        if upgrade_success:
            print("\n" + "=" * 50)
            print("🎉 All database upgrades completed successfully!")
            print("✅ Your Otithi database is now up to date")
            print("\n📝 Summary of changes:")
            print("   • Added 'admin' user type")
            print("   • Added missing columns (password_hash, bio, verified, rating, reviews_count)")
            print("   • Created default admin user (if needed)")
            print("\n🔐 Admin Login Details:")
            print("   📧 Email: admin@otithi.com")
            print("   🔑 Password: admin123")
            print("   ⚠️  Change password after first login!")
        else:
            print("\n❌ Some upgrades failed. Please check the errors above.")
            return False
            
    except Exception as e:
        print(f"❌ Unexpected error during upgrade: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("\n🔌 Database connection closed")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
