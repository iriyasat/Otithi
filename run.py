from app import create_app
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    app = create_app()
    logger.info("Flask app created successfully")
except Exception as e:
    logger.error(f"Failed to create Flask app: {e}")
    raise

if __name__ == '__main__':
    try:
        # Use environment variable for debug mode, default to False for production
        debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        
        logger.info(f"Starting Flask app on {host}:{port} (debug={debug_mode})")
        app.run(host=host, port=port, debug=debug_mode)
    except Exception as e:
        logger.error(f"Failed to start Flask app: {e}")
        raise
