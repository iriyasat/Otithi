# Routes package initialization

def register_blueprints(app):
    """Register all blueprints with the Flask app in proper order"""
    blueprints_registered = 0
    failed_blueprints = []
    
    # Register blueprints in logical order: core, auth, features, admin
    blueprint_configs = [
        ('main', 'main_bp', 'Main'),
        ('auth', 'auth_bp', 'Auth'),
        ('api', 'api_bp', 'API'),
        ('listings', 'listings_bp', 'Listings'),
        ('bookings', 'bookings_bp', 'Bookings'),
        ('profile', 'profile_bp', 'Profile'),
        ('messages', 'messages_bp', 'Messages'),
        ('admin', 'admin_bp', 'Admin'),
    ]
    
    for module_name, blueprint_name, display_name in blueprint_configs:
        try:
            module = __import__(f'app.routes.{module_name}', fromlist=[blueprint_name])
            blueprint = getattr(module, blueprint_name)
            app.register_blueprint(blueprint)
            blueprints_registered += 1
            print(f"✓ {display_name} blueprint registered")
        except ImportError as e:
            failed_blueprints.append(f"{display_name} (ImportError: {e})")
            print(f"⚠ {display_name} blueprint not found: {e}")
        except AttributeError as e:
            failed_blueprints.append(f"{display_name} (AttributeError: {e})")
            print(f"⚠ {display_name} blueprint attribute error: {e}")
        except Exception as e:
            failed_blueprints.append(f"{display_name} (Error: {e})")
            print(f"⚠ {display_name} blueprint failed to register: {e}")
    
    print(f"✓ Total blueprints registered: {blueprints_registered}")
    
    if blueprints_registered == 0:
        print("❌ No blueprints could be registered! App will use fallback routes.")
        raise ImportError("No blueprints could be registered")
    
    if failed_blueprints:
        print(f"⚠ Failed to register: {', '.join(failed_blueprints)}")
    
    return blueprints_registered
