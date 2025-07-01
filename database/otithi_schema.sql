-- =====================================================
-- Otithi Database Schema - Simplified Version
-- Bangladeshi Hospitality Platform Database
-- =====================================================

-- Create database
CREATE DATABASE IF NOT EXISTS otithi
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE otithi;

-- 1. Users Table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    user_type ENUM('guest', 'host') DEFAULT 'guest',
    profile_photo TEXT,
    join_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Listings Table
CREATE TABLE listings (
    listing_id INT AUTO_INCREMENT PRIMARY KEY,
    host_id INT NOT NULL,
    title VARCHAR(255),
    description TEXT,
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100),
    room_type ENUM('entire_place', 'private_room', 'shared_room') DEFAULT 'entire_place',
    price_per_night DECIMAL(10,2),
    max_guests INT,
    amenities TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (host_id) REFERENCES users(user_id)
);

-- 3. Bookings Table
CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    listing_id INT NOT NULL,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    total_price DECIMAL(10,2),
    status ENUM('pending', 'confirmed', 'cancelled') DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (listing_id) REFERENCES listings(listing_id)
);

-- 4. Reviews Table
CREATE TABLE reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    reviewer_id INT NOT NULL,
    listing_id INT NOT NULL,
    rating DECIMAL(2,1) CHECK (rating >= 0.0 AND rating <= 5.0),
    comments TEXT,
    review_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reviewer_id) REFERENCES users(user_id),
    FOREIGN KEY (listing_id) REFERENCES listings(listing_id)
);

-- 5. Payments Table
CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    booking_id INT NOT NULL,
    amount DECIMAL(10,2),
    payment_method ENUM('card', 'paypal', 'bank_transfer') DEFAULT 'card',
    payment_status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
);

-- 6. Location Table (Optional)
CREATE TABLE locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    listing_id INT NOT NULL,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    city VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    FOREIGN KEY (listing_id) REFERENCES listings(listing_id)
);

-- Show completion message
SELECT 'Otithi simplified database schema created successfully!' as Status;
