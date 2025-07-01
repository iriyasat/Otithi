#!/usr/bin/env python3
"""
Othiti - Bangladeshi Hospitality Platform
Development Server Runner
"""

from app import create_app
import os

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    # Development server configuration
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    
    app.run(
        host=host,
        port=port,
        debug=debug_mode,
        threaded=True
    ) 