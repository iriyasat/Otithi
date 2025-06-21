#!/usr/bin/env python3
"""
Diagnostic Script for Othiti Flask App
Checks for specific issues like pagination, template errors, etc.
"""

import requests
import re
import sys

BASE_URL = "http://localhost:5000"

def check_server():
    """Check if server is running"""
    try:
        response = requests.get(BASE_URL, timeout=5)
        print("✅ Server is running")
        return True
    except:
        print("❌ Server is not running. Please start with: python run.py")
        return False

def check_listings_page():
    """Check listings page for pagination issues"""
    print("\n🔍 Checking listings page...")
    
    try:
        response = requests.get(f"{BASE_URL}/listings", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Listings page returned status: {response.status_code}")
            return
        
        content = response.text
        
        # Check for pagination errors
        if 'pagination is undefined' in content.lower():
            print("❌ PAGINATION ERROR: 'pagination' is undefined")
        elif 'jinja2.exceptions.undefinederror' in content.lower():
            print("❌ TEMPLATE ERROR: UndefinedError detected")
        else:
            print("✅ No pagination errors detected")
        
        # Check if pagination elements are present (look for actual HTML elements)
        if 'pagination justify-content-center' in content or 'page-item' in content:
            print("✅ Pagination template elements found")
        else:
            print("⚠️  Pagination template elements not found")
        
        # Check for other common template errors
        if 'jinja2.exceptions.templatenotfound' in content.lower():
            print("❌ TEMPLATE ERROR: Template not found")
        
        if 'jinja2.exceptions.templatesyntaxerror' in content.lower():
            print("❌ TEMPLATE ERROR: Template syntax error")
        
        # Check for search functionality
        if 'search' in content and 'location' in content:
            print("✅ Search and filter elements found")
        
        # Check for listing cards
        if 'listing-card' in content:
            print("✅ Listing cards found")
        
    except Exception as e:
        print(f"❌ Error checking listings page: {str(e)}")

def check_listing_detail():
    """Check listing detail page"""
    print("\n🔍 Checking listing detail page...")
    
    try:
        response = requests.get(f"{BASE_URL}/listing/1", timeout=10)
        
        if response.status_code == 200:
            print("✅ Listing detail page loads successfully")
        elif response.status_code == 404:
            print("⚠️  Listing detail page returns 404 (no listing with ID 1)")
        else:
            print(f"❌ Listing detail page returned status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking listing detail: {str(e)}")

def check_auth_pages():
    """Check authentication pages"""
    print("\n🔍 Checking authentication pages...")
    
    auth_pages = [
        ('/auth/login', 'Login'),
        ('/auth/register', 'Register')
    ]
    
    for route, name in auth_pages:
        try:
            response = requests.get(f"{BASE_URL}{route}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {name} page loads successfully")
            else:
                print(f"❌ {name} page returned status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error checking {name} page: {str(e)}")

def check_protected_routes():
    """Check that protected routes redirect to login"""
    print("\n🔍 Checking protected routes...")
    
    protected_routes = [
        ('/user/profile', 'User Profile'),
        ('/user/my-bookings', 'User Bookings'),
        ('/host/dashboard', 'Host Dashboard'),
        ('/admin/dashboard', 'Admin Dashboard'),
        ('/messages', 'Messages')
    ]
    
    for route, name in protected_routes:
        try:
            response = requests.get(f"{BASE_URL}{route}", timeout=10, allow_redirects=False)
            if response.status_code == 302:
                print(f"✅ {name} correctly redirects (protected)")
            else:
                print(f"⚠️  {name} returned status: {response.status_code} (should redirect)")
        except Exception as e:
            print(f"❌ Error checking {name}: {str(e)}")

def check_listing_parameters():
    """Check listings page with various parameters"""
    print("\n🔍 Checking listings with parameters...")
    
    params = [
        ('search=test', 'Search parameter'),
        ('location=Dhaka', 'Location parameter'),
        ('sort=price_asc', 'Price ascending sort'),
        ('sort=price_desc', 'Price descending sort'),
        ('sort=newest', 'Newest sort'),
        ('sort=oldest', 'Oldest sort'),
        ('page=1', 'Page 1'),
        ('page=2', 'Page 2')
    ]
    
    for param, description in params:
        try:
            response = requests.get(f"{BASE_URL}/listings?{param}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {description} works")
            else:
                print(f"❌ {description} returned status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error with {description}: {str(e)}")

def check_static_files():
    """Check if static files are accessible"""
    print("\n🔍 Checking static files...")
    
    static_files = [
        '/static/css/base.css',
        '/static/css/components.css',
        '/static/css/layout.css',
        '/static/js/main.js',
        '/static/images/default-listing.svg'
    ]
    
    for file_path in static_files:
        try:
            response = requests.get(f"{BASE_URL}{file_path}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {file_path} accessible")
            else:
                print(f"❌ {file_path} returned status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error checking {file_path}: {str(e)}")

def main():
    print("🔧 Othiti Flask App Diagnostic Tool")
    print("=" * 50)
    
    if not check_server():
        sys.exit(1)
    
    check_listings_page()
    check_listing_detail()
    check_auth_pages()
    check_protected_routes()
    check_listing_parameters()
    check_static_files()
    
    print("\n" + "=" * 50)
    print("✅ Diagnostic complete!")
    print("\nIf you see any ❌ errors above, those need to be fixed.")
    print("If you see ⚠️ warnings, those might need attention.")

if __name__ == "__main__":
    main() 