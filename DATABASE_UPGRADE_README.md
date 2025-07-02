# Database Upgrade Scripts

This folder contains automated scripts for managing Otithi database upgrades.

## Scripts

### 1. `upgrade_database.py` - Automated Database Upgrade
Automatically applies all necessary database schema updates.

**Usage:**
```bash
python upgrade_database.py
```

**What it does:**
- Adds 'admin' to user_type ENUM
- Adds missing columns (password_hash, bio, verified, rating, reviews_count)
- Creates default admin user if none exists

### 2. `create_admin.py` - Create Admin User
Interactive script to create or update a user to admin.

**Usage:**
```bash
python create_admin.py
```

**Features:**
- Interactive prompts for user details
- Can create new admin or update existing user
- Default admin: admin@otithi.com / admin123

## Quick Setup

For a fresh installation:

1. Run database upgrade:
   ```bash
   python upgrade_database.py
   ```

2. (Optional) Create custom admin:
   ```bash
   python create_admin.py
   ```

3. Start the application:
   ```bash
   python run.py
   ```

4. Login as admin:
   - Email: admin@otithi.com
   - Password: admin123

## Default Admin Account

After running the upgrade, you can login with:
- **Email:** admin@otithi.com  
- **Password:** admin123
- **⚠️ Change password after first login!**

## Database Schema Updates

The upgrade script handles these schema changes automatically:
- Users table: Adds admin user type, password_hash, bio, verified columns
- Listings table: Adds rating, reviews_count columns
- Ensures all foreign key relationships are maintained
