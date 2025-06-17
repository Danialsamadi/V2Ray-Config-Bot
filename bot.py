#!/usr/bin/env python3
import os
import json
import logging
from datetime import datetime, timezone, timedelta
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv
import re  # Add this import at the top of the file
import requests  # Add this import at the top of the file
import asyncio  # Add this import at the top of the file

# Load environment variables from .env file
load_dotenv()

# Load environment variables with defaults
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
MAX_PROXIES = int(os.getenv('MAX_PROXIES', 100))
PROXY_SOURCE_URL = os.getenv('PROXY_SOURCE_URL', 'https://raw.githubusercontent.com/soroushmirzaei/telegram-proxies-collector/main/proxies')
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO'))
)
logger = logging.getLogger(__name__)

async def send_proxies_to_channel():
    """Send the latest proxies to the specified Telegram channel."""
    if not BOT_TOKEN or not CHANNEL_ID:
        logger.error("Missing environment variables: TELEGRAM_BOT_TOKEN or TELEGRAM_CHANNEL_ID")
        return False
    
    try:
        bot = Bot(token=BOT_TOKEN)
        
        # Get current datetime in Iran timezone
        current_datetime = datetime.now(tz=timezone(timedelta(hours=3, minutes=30)))
        datetime_str = current_datetime.strftime("%a, %d %b %Y %X %Z")
        
        # Fetch latest proxies from online source
        try:
            response = requests.get(PROXY_SOURCE_URL, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()  # Raise an exception for bad status codes
            content = response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch proxies: {e}")
            # Fallback to local file if online fetch fails
            with open('./proxies', 'r') as file:
                content = file.read()
        
        # Extract all proxy links using regex
        proxy_links = re.findall(r'(tg://proxy\?[^\s]+)', content)
        
        # Remove duplicate links while preserving order and first occurrence
        seen_links = set()
        unique_proxy_links = []
        for link in proxy_links:
            # Normalize the link by removing any trailing '=' characters
            normalized_link = link.rstrip('=')
            
            # Add to unique links if not seen before
            if normalized_link not in seen_links:
                seen_links.add(normalized_link)
                unique_proxy_links.append(link)
        
        # Update proxy_links with unique links
        proxy_links = unique_proxy_links
        
        # Limit the number of proxy links
        proxy_links = proxy_links[:MAX_PROXIES]
        
        # Prepare the first message with summary
        first_message = f"🔄 *Latest Proxies Update: {datetime_str}*\n\n"
        first_message += f"*Total Proxies in Source:* {len(re.findall(r'(tg://proxy\?[^\s]+)', content))}\n"
        first_message += f"*Proxies Displayed:* {len(proxy_links)}\n\n"
        
        # Add subscription links to the first message
        first_message += "*Subscription Links:*\n"
        first_message += "• [All Proxies](https://raw.githubusercontent.com/soroushmirzaei/telegram-proxies-collector/main/proxies)\n"
        first_message += "• [IPv4 Proxies](https://raw.githubusercontent.com/soroushmirzaei/telegram-proxies-collector/main/layers/ipv4)\n"
        first_message += "• [IPv6 Proxies](https://raw.githubusercontent.com/soroushmirzaei/telegram-proxies-collector/main/layers/ipv6)\n"
        first_message += "• [Web Interface](https://soroushmirzaei.github.io/telegram-proxies-collector)\n"
        
        # Send the first message
        try:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=first_message,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            await asyncio.sleep(1)  # Add a small delay
        except Exception as e:
            logger.error(f"Failed to send first message: {e}")
            return False
        
        # Prepare and send proxy links in batches
        batch_size = 10  # Number of proxies per message
        total_batches = (len(proxy_links) + batch_size - 1) // batch_size
        
        for batch in range(total_batches):
            # Calculate start and end indices for this batch
            start_idx = batch * batch_size
            end_idx = min((batch + 1) * batch_size, len(proxy_links))
            batch_links = proxy_links[start_idx:end_idx]
            
            # Prepare batch message
            current_message = f"*Proxy Links ({batch + 1}/{total_batches}):*\n"
            for i, link in enumerate(batch_links, start=1):
                current_message += f"---------------\n"
                current_message += f"[Proxy {i}]({link})\n"
                current_message += f"---------------\n"
            
            # Send batch message with error handling and delay
            try:
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=current_message,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                await asyncio.sleep(1)  # Add a small delay between messages
            except Exception as e:
                logger.error(f"Failed to send batch {batch + 1}: {e}")
                # Continue with next batch if one fails
                continue
        
        # Send comprehensive subscription links in a final message
        subscription_message = "*Comprehensive Proxy Resources:*\n\n"
        
        subscription_message += "*Subscription Links:*\n"
        subscription_message += "• [All Proxies](https://raw.githubusercontent.com/soroushmirzaei/telegram-proxies-collector/main/proxies)\n"
        subscription_message += "• [IPv4 Proxies](https://raw.githubusercontent.com/soroushmirzaei/telegram-proxies-collector/main/layers/ipv4)\n"
        subscription_message += "• [IPv6 Proxies](https://raw.githubusercontent.com/soroushmirzaei/telegram-proxies-collector/main/layers/ipv6)\n"
        
        subscription_message += "\n*Additional Resources:*\n"
        subscription_message += "• [Web Interface](https://soroushmirzaei.github.io/telegram-proxies-collector)\n"
        subscription_message += "• [GitHub Repository](https://github.com/soroushmirzaei/telegram-proxies-collector)\n"
        
        subscription_message += "\n*How to Use:*\n"
        subscription_message += "1. Copy proxy links\n"
        subscription_message += "2. Import into your preferred V2Ray client\n"
        subscription_message += "3. Connect and browse freely\n"
        
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=subscription_message,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
        
        logger.info(f"Successfully sent proxies to channel {CHANNEL_ID}")
        return True
        
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(send_proxies_to_channel()) 