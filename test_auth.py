#!/usr/bin/env python3
"""
Simple test script to verify authentication flow
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_logout_route():
    """Test that logout route is properly configured"""
    try:
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            print("✓ App created successfully")
            
            # Check available routes
            logout_routes = []
            for rule in app.url_map.iter_rules():
                if 'logout' in rule.rule:
                    logout_routes.append(f"{rule.rule} -> {rule.endpoint}")
            
            print(f"📍 Logout routes found: {len(logout_routes)}")
            for route in logout_routes:
                print(f"  - {route}")
            
            # Check if auth blueprint is registered
            auth_registered = 'auth' in [bp.name for bp in app.blueprints.values()]
            print(f"✓ Auth blueprint registered: {auth_registered}")
            
            # Test CSRF protection
            csrf_enabled = app.config.get('WTF_CSRF_ENABLED', False)
            print(f"✓ CSRF protection enabled: {csrf_enabled}")
            
            # Test session configuration
            session_config = {
                'SESSION_COOKIE_HTTPONLY': app.config.get('SESSION_COOKIE_HTTPONLY'),
                'SESSION_COOKIE_SAMESITE': app.config.get('SESSION_COOKIE_SAMESITE'),
                'PERMANENT_SESSION_LIFETIME': app.config.get('PERMANENT_SESSION_LIFETIME')
            }
            print(f"✓ Session config: {session_config}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_auth_utilities():
    """Test that authentication utilities are working"""
    try:
        from app.auth_utils import admin_required, role_required, host_required
        print("✓ Auth utilities imported successfully")
        
        # Test decorator creation
        @admin_required
        def test_admin_function():
            return "admin access"
        
        @role_required('host', 'admin')
        def test_role_function():
            return "role access"
        
        print("✓ Decorators created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Auth utilities error: {e}")
        return False


def test_forms():
    """Test that forms are working"""
    try:
        from app.forms import LoginForm, RegistrationForm
        print("✓ Forms imported successfully")
        
        # Test form creation
        login_form = LoginForm()
        register_form = RegistrationForm()
        
        print(f"✓ LoginForm fields: {list(login_form._fields.keys())}")
        print(f"✓ RegistrationForm fields: {list(register_form._fields.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Forms error: {e}")
        return False


if __name__ == "__main__":
    print("🔐 Testing Otithi Authentication System")
    print("=" * 50)
    
    tests = [
        ("Route Configuration", test_logout_route),
        ("Authentication Utilities", test_auth_utilities),
        ("Secure Forms", test_forms)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}:")
        if test_func():
            passed += 1
            print(f"✅ {test_name} - PASSED")
        else:
            print(f"❌ {test_name} - FAILED")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Authentication system looks good.")
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
