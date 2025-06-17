#!/usr/bin/env python3
import os
import sys
import logging
import traceback
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot_run.log')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def main():
    try:
        from bot import send_proxies_to_channel
        import asyncio

        logger.info("Starting proxy collection...")
        
        # Run the async function
        result = asyncio.run(send_proxies_to_channel())
        
        if result:
            logger.info("Successfully collected and sent proxies")
            sys.exit(0)
        else:
            logger.error("Failed to collect or send proxies")
            sys.exit(1)
    
    except Exception as e:
        logger.error("Unexpected error occurred:")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 