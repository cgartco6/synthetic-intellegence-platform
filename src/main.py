#!/usr/bin/env python3
"""
Synthetic Intelligence Platform - Main Entry Point
"""

import asyncio
import logging
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.web.app import AIPlatformApp

async def main():
    """Main application entry point"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('ai_platform.log')
        ]
    )
    
    logger = logging.getLogger("main")
    
    try:
        logger.info("Starting Synthetic Intelligence Platform...")
        
        # Create and run the application
        app = AIPlatformApp()
        
        logger.info("Platform started successfully")
        logger.info("Access the web interface at http://localhost:5000")
        
        # Run Flask app
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except KeyboardInterrupt:
        logger.info("Shutting down platform...")
    except Exception as e:
        logger.error(f"Platform failed to start: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
