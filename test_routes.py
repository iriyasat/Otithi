#!/usr/bin/env python3
"""
Simple Route Testing Script for Othiti Flask App
"""

import requests
import sys

BASE_URL = "http://localhost:5000"

def test_route(route, expected_status=200):
    """Test a single route"""
    url = f"{BASE_URL}{route}"
    try:
        response = requests.get(url, timeout=10, allow_redirects=False)
        if response.status_code == expected_status:
            print(f"✅ {route} - Status: {response.status_code}")
            return True
        elif expected_status == 302 and response.status_code in [302, 308]:
            print(f"✅ {route} - Status: {response.status_code} (redirect as expected)")
            return True
        elif response.status_code in [302, 308] and expected_status not in [302, 308]:
            print(f"⚠️  {route} - Unexpected redirect: {response.status_code}")
            return False
        else:
            print(f"❌ {route} - Expected: {expected_status}, Got: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {route} - Connection Error: Server not running?")
        return False
    except Exception as e:
        print(f"❌ {route} - Error: {str(e)}")
        return False

def main():
    print("🚀 Testing Othiti Flask App Routes")
    print("=" * 50)
    
    # Test public routes
    print("\n🔍 Public Routes:")
    public_routes = [
        ('/', 200),
        ('/about', 200),
        ('/listings', 200),
        ('/listing/1', 200),
        ('/auth/login', 200),
        ('/auth/register', 200),
    ]
    
    for route, expected in public_routes:
        test_route(route, expected)
    
    # Test protected routes (should redirect to login)
    print("\n🔒 Protected Routes (should redirect):")
    protected_routes = [
        ('/user/profile', 302),
        ('/user/my-bookings', 302),
        ('/host/dashboard', 302),
        ('/admin/dashboard', 302),
        ('/messages', 302),
    ]
    
    for route, expected in protected_routes:
        test_route(route, expected)
    
    # Test listing routes with parameters
    print("\n🏠 Listing Routes with Parameters:")
    listing_routes = [
        ('/listings?search=test', 200),
        ('/listings?location=Dhaka', 200),
        ('/listings?sort=price_asc', 200),
        ('/listings?page=1', 200),
    ]
    
    for route, expected in listing_routes:
        test_route(route, expected)
    
    print("\n✅ Testing complete!")

if __name__ == "__main__":
    main() 