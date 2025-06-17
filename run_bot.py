#!/usr/bin/env python3
import os
import sys
import time
import logging
import subprocess
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO'))
)
logger = logging.getLogger(__name__)

# Import after dotenv to ensure environment variables are loaded
from bot import send_proxies_to_channel

async def main():
    """Run the proxy collection script and then post to Telegram channel."""
    try:
        # Check if environment variables are set
        if not os.environ.get('TELEGRAM_BOT_TOKEN') or not os.environ.get('TELEGRAM_CHANNEL_ID'):
            logger.warning("Missing environment variables: TELEGRAM_BOT_TOKEN or TELEGRAM_CHANNEL_ID")
            logger.info("You can still run the proxy collection without posting to Telegram")
        
        # Run the main proxy collection script
        logger.info("Starting proxy collection...")
        result = subprocess.run(['python3', 'main.py'], check=True)
        
        if result.returncode != 0:
            logger.error("Proxy collection failed")
            return
        
        logger.info("Proxy collection completed successfully")
        
        # Wait a moment to ensure files are written
        time.sleep(2)
        
        # Post to Telegram channel if environment variables are set
        if os.environ.get('TELEGRAM_BOT_TOKEN') and os.environ.get('TELEGRAM_CHANNEL_ID'):
            logger.info("Posting proxies to Telegram channel...")
            success = await send_proxies_to_channel()
            if success:
                logger.info("Successfully posted proxies to Telegram channel")
            else:
                logger.error("Failed to post proxies to Telegram channel")
        else:
            logger.info("Skipping Telegram posting due to missing environment variables")
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running proxy collection: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 