#!/usr/bin/env python3
"""
Azure App Service startup script for Mimir API
This script initializes the application for Azure App Service deployment
"""

import os
import sys
import logging
from pathlib import Path

# Add the application directory to Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_azure_environment():
    """Set up Azure App Service specific environment"""
    
    # Create necessary directories
    directories = [
        '/tmp/chromadb',
        '/tmp/uploads',
        '/tmp/data',
        '/tmp/logs',
        '/tmp/face_images'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    # Set Azure-specific environment variables
    os.environ.setdefault('CHROMADB_LOC', '/tmp/chromadb')
    os.environ.setdefault('USER_DATA_DIR', '/tmp/data')
    os.environ.setdefault('UPLOAD_DIR', '/tmp/uploads')
    os.environ.setdefault('FACE_TEMP_DIR', '/tmp/face_images')
    os.environ.setdefault('LOG_FILE', '/tmp/logs/mimir-api.log')
    os.environ.setdefault('APP_ENV', 'production')
    
    logger.info("Azure App Service environment setup completed")

def get_application():
    """Get the FastAPI application instance"""
    try:
        # Setup Azure environment
        setup_azure_environment()
        
        # Import and return the FastAPI app
        from app.dependencies import app
        logger.info("FastAPI application loaded successfully")
        return app
        
    except Exception as e:
        logger.error(f"Failed to load application: {str(e)}")
        raise

# For Azure App Service
app = get_application()

if __name__ == "__main__":
    # This is for local testing
    import uvicorn
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
