#!/usr/bin/env python3
import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

# Configure logging before importing other modules
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_run.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import after logging configuration
from bot import send_proxies_to_channel

async def main():
    try:
        logger.info("Starting proxy update process")
        
        # Validate required environment variables
        required_vars = ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHANNEL_ID', 'PROXY_SOURCE_URL']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            return 1
        
        # Run the proxy update
        success = await send_proxies_to_channel()
        
        if success:
            logger.info("Proxy update completed successfully")
            return 0
        else:
            logger.error("Proxy update failed")
            return 1
    
    except Exception as e:
        logger.exception(f"Unexpected error during proxy update: {e}")
        return 1

if __name__ == '__main__':
    try:
        # Run the async main function
        result = asyncio.run(main())
        sys.exit(result)
    except Exception as e:
        logger.exception(f"Critical error: {e}")
        sys.exit(1) 