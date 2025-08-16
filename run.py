from app import create_app
from app.routes.messages import init_socketio
import os
import sys

def main():
    """Main application entry point with comprehensive error handling"""
    
    print("🚀 Starting Otithi Application...")
    
    try:
        # Step 1: Create Flask app
        print("📱 Creating Flask application...")
        app = create_app()
        print("✅ Flask app created successfully")
        
    except ImportError as e:
        print(f"❌ Import Error: Could not import required modules")
        print(f"   Details: {e}")
        print("   Solution: Make sure all dependencies are installed (pip install -r requirements.txt)")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ App Creation Error: Failed to create Flask application")
        print(f"   Details: {e}")
        print("   Solution: Check your app configuration and database settings")
        sys.exit(1)
    
    try:
        # Step 2: Initialize SocketIO
        print("🔗 Initializing real-time messaging (SocketIO)...")
        socketio = init_socketio(app)
        print("✅ SocketIO initialized successfully")
        
    except Exception as e:
        print(f"❌ SocketIO Error: Failed to initialize real-time messaging")
        print(f"   Details: {e}")
        print("   Solution: Check your messages route configuration")
        sys.exit(1)
    
    try:
        # Step 3: Get configuration
        debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        
        print(f"⚙️  Configuration:")
        print(f"   • Host: {host}")
        print(f"   • Port: {port}")
        print(f"   • Debug Mode: {debug_mode}")
        print(f"   • Environment: {'Development' if debug_mode else 'Production'}")
        
    except ValueError as e:
        print(f"❌ Configuration Error: Invalid port number")
        print(f"   Details: {e}")
        print("   Solution: Set PORT environment variable to a valid number (e.g., 5000)")
        sys.exit(1)
    
    try:
        # Step 4: Start the server
        print(f"\n🌟 Starting Otithi server...")
        print(f"📍 Application will be available at: http://{host}:{port}")
        print(f"🔧 Admin panel: http://{host}:{port}/admin")
        print(f"🔑 Admin login: admin@otithi.com")
        print("\n" + "="*50)
        print("✨ OTITHI IS READY! ✨")
        print("="*50 + "\n")
        
        # Start the application
        socketio.run(app, host=host, port=port, debug=debug_mode, allow_unsafe_werkzeug=True)
        
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port Error: Port {port} is already in use")
            print(f"   Solution: Either:")
            print(f"   • Stop the application using port {port}")
            print(f"   • Use a different port: PORT=5001 python run.py")
        else:
            print(f"❌ Network Error: {e}")
            print("   Solution: Check your network configuration")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Application stopped by user (Ctrl+C)")
        print("👋 Goodbye!")
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Startup Error: Failed to start the server")
        print(f"   Details: {e}")
        print("   Solution: Check the error details above and your system configuration")
        sys.exit(1)

if __name__ == '__main__':
    main()
