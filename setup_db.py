from app import create_app, db
from app.models import User, Listing, Booking, Review, Conversation, Message
import pymysql

def setup_database():
    """Set up the database tables and verify their existence"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Tables created successfully!")
        
        # Connect directly to MySQL to verify tables
        conn = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='',
            database='otithi_db'
        )
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                print("\n📊 Existing Tables:")
                for table in tables:
                    print(f"  • {table[0]}")
                
                # Verify specific tables we need (using singular form as in the database)
                required_tables = ['user', 'listing', 'booking', 'review', 'conversation', 'message']
                existing_tables = [t[0] for t in tables]
                
                print("\n🔍 Verification:")
                all_tables_exist = True
                for table in required_tables:
                    if table in existing_tables:
                        print(f"  ✅ {table} table exists")
                    else:
                        print(f"  ❌ {table} table is missing")
                        all_tables_exist = False
                
                if all_tables_exist:
                    print("\n✨ Success! All required tables are present in the database.")
                else:
                    print("\n⚠️ Warning: Some required tables are missing!")
                
                # Show table structures for verification
                print("\n📋 Table Structures:")
                for table in existing_tables:
                    cursor.execute(f"DESCRIBE {table}")
                    structure = cursor.fetchall()
                    print(f"\n{table} table:")
                    for column in structure:
                        print(f"  • {column[0]}: {column[1]}")
                
        finally:
            conn.close()

if __name__ == '__main__':
    setup_database() 