from app import create_app, db
import pymysql
import shortuuid

def migrate_to_uuid():
    """Migrate database tables to use UUID primary keys"""
    app = create_app()
    
    with app.app_context():
        # Connect to MySQL
        conn = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='',
            database='otithi_db'
        )
        
        try:
            with conn.cursor() as cursor:
                # Drop existing tables (since we're starting fresh)
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                for table in tables:
                    cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                conn.commit()
                
                # Create tables with UUID columns
                cursor.execute("""
                    CREATE TABLE user (
                        id VARCHAR(22) PRIMARY KEY,
                        username VARCHAR(64) UNIQUE NOT NULL,
                        email VARCHAR(120) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        role ENUM('guest', 'host', 'admin') NOT NULL DEFAULT 'guest',
                        is_verified BOOLEAN DEFAULT FALSE,
                        is_active BOOLEAN DEFAULT TRUE,
                        profile_picture VARCHAR(255),
                        nid_filename VARCHAR(255),
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        last_login DATETIME,
                        INDEX idx_username (username),
                        INDEX idx_email (email),
                        INDEX idx_role (role),
                        INDEX idx_created_at (created_at)
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
                """)
                
                cursor.execute("""
                    CREATE TABLE listing (
                        id VARCHAR(22) PRIMARY KEY,
                        name VARCHAR(200) NOT NULL,
                        description TEXT NOT NULL,
                        location VARCHAR(200) NOT NULL,
                        price_per_night DECIMAL(10,2) NOT NULL,
                        guest_capacity INT NOT NULL DEFAULT 1,
                        status ENUM('draft', 'pending', 'approved', 'rejected', 'inactive') NOT NULL DEFAULT 'pending',
                        approved BOOLEAN DEFAULT FALSE,
                        image_filename VARCHAR(255),
                        host_id VARCHAR(22) NOT NULL,
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_host_id (host_id),
                        INDEX idx_location (location),
                        INDEX idx_status (status),
                        INDEX idx_price (price_per_night),
                        FOREIGN KEY (host_id) REFERENCES user(id) ON DELETE CASCADE
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
                """)
                
                cursor.execute("""
                    CREATE TABLE booking (
                        id VARCHAR(22) PRIMARY KEY,
                        guest_id VARCHAR(22) NOT NULL,
                        listing_id VARCHAR(22) NOT NULL,
                        check_in_date DATE NOT NULL,
                        check_out_date DATE NOT NULL,
                        guest_count INT NOT NULL DEFAULT 1,
                        total_price DECIMAL(10,2) NOT NULL,
                        status ENUM('pending', 'confirmed', 'checked_in', 'checked_out', 'cancelled') NOT NULL DEFAULT 'pending',
                        nid_filename VARCHAR(255),
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        confirmed_at DATETIME,
                        checked_in_at DATETIME,
                        checked_out_at DATETIME,
                        INDEX idx_guest_id (guest_id),
                        INDEX idx_listing_id (listing_id),
                        INDEX idx_status (status),
                        INDEX idx_dates (check_in_date, check_out_date),
                        FOREIGN KEY (guest_id) REFERENCES user(id) ON DELETE CASCADE,
                        FOREIGN KEY (listing_id) REFERENCES listing(id) ON DELETE CASCADE
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
                """)
                
                cursor.execute("""
                    CREATE TABLE review (
                        id VARCHAR(22) PRIMARY KEY,
                        reviewer_id VARCHAR(22) NOT NULL,
                        reviewee_id VARCHAR(22) NOT NULL,
                        listing_id VARCHAR(22) NOT NULL,
                        booking_id VARCHAR(22) NOT NULL UNIQUE,
                        rating INT NOT NULL,
                        comment TEXT,
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_reviewer_id (reviewer_id),
                        INDEX idx_reviewee_id (reviewee_id),
                        INDEX idx_listing_id (listing_id),
                        INDEX idx_booking_id (booking_id),
                        FOREIGN KEY (reviewer_id) REFERENCES user(id) ON DELETE CASCADE,
                        FOREIGN KEY (reviewee_id) REFERENCES user(id) ON DELETE CASCADE,
                        FOREIGN KEY (listing_id) REFERENCES listing(id) ON DELETE CASCADE,
                        FOREIGN KEY (booking_id) REFERENCES booking(id) ON DELETE CASCADE
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
                """)
                
                cursor.execute("""
                    CREATE TABLE conversation (
                        id VARCHAR(22) PRIMARY KEY,
                        user1_id VARCHAR(22) NOT NULL,
                        user2_id VARCHAR(22) NOT NULL,
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        last_message_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        INDEX idx_user1_id (user1_id),
                        INDEX idx_user2_id (user2_id),
                        INDEX idx_last_message (last_message_at),
                        FOREIGN KEY (user1_id) REFERENCES user(id) ON DELETE CASCADE,
                        FOREIGN KEY (user2_id) REFERENCES user(id) ON DELETE CASCADE
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
                """)
                
                cursor.execute("""
                    CREATE TABLE message (
                        id VARCHAR(22) PRIMARY KEY,
                        conversation_id VARCHAR(22) NOT NULL,
                        sender_id VARCHAR(22) NOT NULL,
                        recipient_id VARCHAR(22) NOT NULL,
                        content TEXT NOT NULL,
                        is_read BOOLEAN DEFAULT FALSE,
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_conversation_id (conversation_id),
                        INDEX idx_sender_id (sender_id),
                        INDEX idx_recipient_id (recipient_id),
                        INDEX idx_is_read (is_read),
                        FOREIGN KEY (conversation_id) REFERENCES conversation(id) ON DELETE CASCADE,
                        FOREIGN KEY (sender_id) REFERENCES user(id) ON DELETE CASCADE,
                        FOREIGN KEY (recipient_id) REFERENCES user(id) ON DELETE CASCADE
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
                """)
                
                # Create admin user
                admin_id = shortuuid.uuid()
                cursor.execute("""
                    INSERT INTO user (id, username, email, password_hash, role, is_verified, is_active)
                    VALUES (%s, %s, %s, %s, %s, 1, 1)
                """, (
                    admin_id,
                    'admin',
                    'admin@otithi.com',
                    'pbkdf2:sha256:600000$dQX3uFAyGHKiYGY9$505bb7f815b88f302554327f1f5bcfc729d338e81d1b366460f816f8fc3d9913',  # Password: admin123
                    'admin'
                ))
                
                conn.commit()
                print("✅ Database migrated to UUID schema successfully!")
                print("\n👤 Admin user created:")
                print("  Username: admin")
                print("  Password: admin123")
                print("  Email: admin@otithi.com")
                
        finally:
            conn.close()

if __name__ == '__main__':
    migrate_to_uuid() 