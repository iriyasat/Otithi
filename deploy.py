#!/usr/bin/env python3
"""
Production deployment script for Otithi
Run this script to prepare the application for production
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a shell command with error handling"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def check_environment():
    """Check if the environment is ready for production"""
    print("🔍 Checking production environment...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    
    # Check if required environment variables are set
    required_env_vars = ['SECRET_KEY', 'MYSQL_HOST', 'MYSQL_DATABASE']
    missing_vars = []
    
    for var in required_env_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your production environment")
    
    print("✅ Environment check completed")
    return True

def install_dependencies():
    """Install production dependencies"""
    return run_command("pip install -r requirements.txt", "Installing dependencies")

def create_upload_directories():
    """Create necessary upload directories"""
    directories = [
        "app/static/uploads/listings",
        "app/static/uploads/profiles",
        "app/static/uploads/temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Upload directories created")
    return True

def set_permissions():
    """Set proper file permissions for production"""
    # Set restrictive permissions on sensitive files
    sensitive_files = ["config.py", "run.py"]
    
    for file in sensitive_files:
        if os.path.exists(file):
            os.chmod(file, 0o600)  # Read/write for owner only
    
    # Set proper permissions for upload directories
    upload_dirs = ["app/static/uploads"]
    for directory in upload_dirs:
        if os.path.exists(directory):
            os.chmod(directory, 0o755)  # Read/write/execute for owner, read/execute for others
    
    print("✅ File permissions set")
    return True

def validate_database_connection():
    """Check if database connection is working"""
    print("🔄 Validating database connection...")
    
    try:
        from app.database import db
        # Try to establish a connection
        result = db.execute_query("SELECT 1 as test")
        if result:
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def run_security_checks():
    """Run basic security checks"""
    print("🔐 Running security checks...")
    
    # Check if SECRET_KEY is set to a production value
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key or 'dev' in secret_key.lower() or len(secret_key) < 32:
        print("⚠️  WARNING: SECRET_KEY should be a strong, unique value for production")
    
    # Check if debug mode is disabled
    from config import Config
    if hasattr(Config, 'DEBUG') and Config.DEBUG:
        print("⚠️  WARNING: Debug mode should be disabled in production")
    
    # Check HTTPS configuration
    if not Config.SESSION_COOKIE_SECURE:
        print("⚠️  WARNING: SESSION_COOKIE_SECURE should be True in production with HTTPS")
    
    print("✅ Security checks completed")
    return True

def main():
    """Main deployment function"""
    print("🚀 Starting Otithi production deployment...")
    print("=" * 50)
    
    steps = [
        check_environment,
        install_dependencies,
        create_upload_directories,
        set_permissions,
        validate_database_connection,
        run_security_checks
    ]
    
    for step in steps:
        if not step():
            print(f"\n❌ Deployment failed at step: {step.__name__}")
            sys.exit(1)
        print()
    
    print("=" * 50)
    print("🎉 Production deployment completed successfully!")
    print("\n📋 Next steps:")
    print("1. Set up a reverse proxy (nginx/Apache)")
    print("2. Configure SSL certificates for HTTPS")
    print("3. Set up process monitoring (systemd/supervisor)")
    print("4. Configure automated backups")
    print("5. Set up log rotation")
    print("\n🔧 To start the application:")
    print("python run.py")

if __name__ == "__main__":
    main()
