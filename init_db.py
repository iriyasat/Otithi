#!/usr/bin/env python3
"""
Database initialization script for Otithi
This script creates the database and tables if they don't exist
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db

def init_database():
    """Initialize the database and create tables"""
    print("Initializing Otithi database...")
    
    try:
        # Database connection is already established in db.__init__
        # Schema will be created automatically if database didn't exist
        
        # Verify tables exist by running a simple query
        tables = db.execute_query("SHOW TABLES")
        table_names = [table[list(table.keys())[0]] for table in tables]
        
        expected_tables = ['users', 'listings', 'bookings', 'reviews']
        missing_tables = [table for table in expected_tables if table not in table_names]
        
        if missing_tables:
            print(f"Missing tables: {missing_tables}")
            print("Please check your database/otithi_schema.sql file")
            return False
        
        print("✅ Database initialized successfully!")
        print(f"✅ Tables found: {table_names}")
        
        # Check if there's any existing data
        user_count = db.execute_query("SELECT COUNT(*) as count FROM users")[0]['count']
        listing_count = db.execute_query("SELECT COUNT(*) as count FROM listings")[0]['count']
        booking_count = db.execute_query("SELECT COUNT(*) as count FROM bookings")[0]['count']
        review_count = db.execute_query("SELECT COUNT(*) as count FROM reviews")[0]['count']
        
        print(f"📊 Current data:")
        print(f"   Users: {user_count}")
        print(f"   Listings: {listing_count}")
        print(f"   Bookings: {booking_count}")
        print(f"   Reviews: {review_count}")
        
        if user_count == 0:
            print("\n💡 Database is empty. This means you'll see real empty data (no dummy data)!")
            print("   You can create users and listings through the web interface.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
