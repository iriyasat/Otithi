#!/usr/bin/env python3
"""
Debug script to test profile page authentication issue
"""
import requests
import sys

def test_profile_access():
    """Test profile page access after login"""
    base_url = "http://127.0.0.1:5000"
    session = requests.Session()
    
    print("🔍 Debugging Profile Page Authentication Issue")
    print("=" * 60)
    
    try:
        # Step 1: Test login
        print("1. Testing login...")
        login_data = {
            'email': 'guest@otithi.com',
            'password': 'password123'
        }
        
        # Get login page first (for CSRF token if needed)
        login_page = session.get(f"{base_url}/login")
        print(f"   Login page status: {login_page.status_code}")
        
        # Attempt login
        login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        print(f"   Login response: {login_response.status_code}")
        print(f"   Location header: {login_response.headers.get('Location', 'None')}")
        
        if login_response.status_code == 302:
            print("   ✅ Login successful")
            
            # Print session cookies
            print(f"   Session cookies: {list(session.cookies.keys())}")
            
            # Step 2: Test profile page access
            print("\n2. Testing profile page access...")
            profile_response = session.get(f"{base_url}/profile", allow_redirects=False)
            print(f"   Profile response: {profile_response.status_code}")
            print(f"   Location header: {profile_response.headers.get('Location', 'None')}")
            
            if profile_response.status_code == 200:
                print("   ✅ Profile page accessible!")
                # Check if content contains expected profile data
                content = profile_response.text
                if "Profile" in content and "guest@otithi.com" in content:
                    print("   ✅ Profile content looks correct")
                else:
                    print("   ⚠️  Profile page loads but content may be incomplete")
                    print(f"   Content preview: {content[:200]}...")
                return True
                
            elif profile_response.status_code == 302:
                redirect_url = profile_response.headers.get('Location', '')
                if 'login' in redirect_url:
                    print("   ❌ Profile redirects to login page")
                    print("   🔍 This indicates authentication failure")
                    
                    # Debug: Check if user loader is working
                    print("\n3. Testing dashboard (for comparison)...")
                    dashboard_response = session.get(f"{base_url}/dashboard", allow_redirects=False)
                    print(f"   Dashboard response: {dashboard_response.status_code}")
                    
                    if dashboard_response.status_code == 200:
                        print("   ✅ Dashboard works - issue is profile-specific")
                    elif dashboard_response.status_code == 302:
                        print("   ❌ Dashboard also redirects - authentication issue")
                    
                else:
                    print(f"   ⚠️  Profile redirects to: {redirect_url}")
                return False
            else:
                print(f"   ❌ Unexpected profile response: {profile_response.status_code}")
                return False
                
        else:
            print("   ❌ Login failed")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask application. Make sure it's running on port 5000.")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_users():
    """Test profile access with different user types"""
    users = [
        {'email': 'guest@otithi.com', 'password': 'password123', 'type': 'Guest'},
        {'email': 'host@otithi.com', 'password': 'password123', 'type': 'Host'},
        {'email': 'admin@otithi.com', 'password': 'admin123', 'type': 'Admin'}
    ]
    
    print("\n🔍 Testing Profile Access for All User Types")
    print("=" * 60)
    
    for user in users:
        print(f"\nTesting {user['type']} user...")
        session = requests.Session()
        base_url = "http://127.0.0.1:5000"
        
        try:
            # Login
            login_response = session.post(f"{base_url}/login", 
                                        data={'email': user['email'], 'password': user['password']}, 
                                        allow_redirects=False)
            
            if login_response.status_code == 302:
                # Test profile
                profile_response = session.get(f"{base_url}/profile", allow_redirects=False)
                if profile_response.status_code == 200:
                    print(f"   ✅ {user['type']} profile works")
                elif profile_response.status_code == 302 and 'login' in profile_response.headers.get('Location', ''):
                    print(f"   ❌ {user['type']} profile redirects to login")
                else:
                    print(f"   ⚠️  {user['type']} profile: {profile_response.status_code}")
            else:
                print(f"   ❌ {user['type']} login failed")
                
        except Exception as e:
            print(f"   ❌ {user['type']} test failed: {e}")

if __name__ == "__main__":
    success = test_profile_access()
    test_multiple_users()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Profile page is working correctly!")
    else:
        print("❌ Profile page has authentication issues that need to be fixed.")
        print("\nPossible causes:")
        print("  1. User loader function not working correctly")
        print("  2. Session cookies not being preserved")
        print("  3. Database connection issues")
        print("  4. Profile route configuration problems")
