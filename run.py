#!/usr/bin/env python
import os
import sys

from app import create_app

app = create_app()

if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    app.run(host=host, port=port, debug=debug)
