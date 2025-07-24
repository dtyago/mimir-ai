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

def get_application():
    """Get the FastAPI application instance"""
    try:
        # Set environment for Azure
        os.environ['ENVIRONMENT'] = 'azure'
        
        # Initialize SQLite compatibility before importing app
        logger.info("Setting up SQLite compatibility...")
        from app.utils.sqlite_compat import setup_sqlite_compatibility
        setup_sqlite_compatibility()
        logger.info("SQLite compatibility setup complete")
        
        # Import and return the FastAPI app
        logger.info("Loading FastAPI application...")
        from app.dependencies import app
        logger.info("FastAPI application loaded successfully")
        return app
        
    except ImportError as e:
        logger.error(f"Import error when loading application: {str(e)}")
        logger.error(f"Current working directory: {os.getcwd()}")
        logger.error(f"Python path: {sys.path}")
        raise
    except Exception as e:
        logger.error(f"Failed to load application: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

# For Azure App Service
app = get_application()

if __name__ == "__main__":
    # This is for local testing - use the universal startup script instead
    logger.info("For local testing, please use: ./start.sh")
    logger.info("This script is intended for Azure App Service only")
    
    import uvicorn
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Starting application on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
