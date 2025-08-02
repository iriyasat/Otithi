-- Insert admin user directly into database
-- Use this if the Python script doesn't work

USE otithi;

-- First, check if admin user already exists
SELECT user_id, name, email, user_type, verified FROM users WHERE email = 'admin@otithi.com';

-- If no admin user exists, insert one
-- Password hash for 'admin123' using werkzeug PBKDF2 method
INSERT INTO users (name, email, password_hash, phone, bio, user_type, join_date, verified) 
VALUES (
    'Administrator',
    'admin@otithi.com',
    'pbkdf2:sha256:260000$PfgmtqVoJ6pJ2G5x$7ec3bb7b4f68b4c79c51ce46d08c36a08e3e41be08a8b5c7a8f3a9c0b8e2da44',
    '+8801234567890',
    'System Administrator for Otithi Platform',
    'admin',
    NOW(),
    TRUE
) ON DUPLICATE KEY UPDATE
    user_type = 'admin',
    verified = TRUE;

-- Verify the admin user was created
SELECT user_id, name, email, user_type, verified FROM users WHERE email = 'admin@otithi.com';

-- Show all users for debugging
SELECT user_id, name, email, user_type, verified FROM users ORDER BY user_id;
