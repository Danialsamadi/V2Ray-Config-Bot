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
import random  # Add this import at the top of the file

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

def fetch_mtproto_data():
    """Fetch data from the MTProto JSON source."""
    url = "https://raw.githubusercontent.com/hookzof/socks5_list/master/tg/mtproto.json"
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch MTProto data: {e}")
        return []

def remove_duplicate_proxies(proxies):
    """Remove duplicate proxies from the list."""
    seen = set()
    unique_proxies = []
    for proxy in proxies:
        if proxy not in seen:
            seen.add(proxy)
            unique_proxies.append(proxy)
    return unique_proxies

async def send_proxies_to_channel():
    """Send the latest proxies to the specified Telegram channel."""
    if not BOT_TOKEN or not CHANNEL_ID:
        logger.error("Missing environment variables: TELEGRAM_BOT_TOKEN or TELEGRAM_CHANNEL_ID")
        return False
    
    try:
        # Increase timeout for requests
        requests.adapters.DEFAULT_TIMEOUT = REQUEST_TIMEOUT
        
        bot = Bot(token=BOT_TOKEN)
        
        # Get current datetime in Iran timezone
        current_datetime = datetime.now(tz=timezone(timedelta(hours=3, minutes=30)))
        datetime_str = current_datetime.strftime("%a, %d %b %Y %X %Z")
        
        # Fetch latest proxies from online source with timeout
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
        
        # Fetch MTProto data
        mtproto_data = fetch_mtproto_data()
        
        # Process MTProto data
        mtproto_links = [f"tg://proxy?server={item['host']}&port={item['port']}&secret={item['secret']}" for item in mtproto_data]
        
        # Combine with existing proxy links
        proxy_links.extend(mtproto_links)
        
        # Remove duplicate proxies
        proxy_links = remove_duplicate_proxies(proxy_links)
        
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
        
        # Calculate half of the proxies
        half_proxies_count = len(proxy_links) // 2
        
        # Limit the proxies to half
        proxy_links = proxy_links[:half_proxies_count]
        
        # Update total_proxies to reflect the new count
        total_proxies = len(proxy_links)
        
        # Prepare the first message with summary
        first_message = f"🔄 *Latest Proxies Update: {datetime_str}*\n\n"
        first_message += f"*Total Proxies in Source:* {total_proxies}\n"
        first_message += f"*Proxies Displayed:* {len(proxy_links)}\n\n"
        
        # Add subscription links to the first message
        first_message += "*Subscription Links:*\n"
        first_message += "• [All Proxies](https://raw.githubusercontent.com/soroushmirzaei/telegram-proxies-collector/main/proxies)\n"
        first_message += "• [IPv4 Proxies](https://raw.githubusercontent.com/soroushmirzaei/telegram-proxies-collector/main/layers/ipv4)\n"
        first_message += "• [IPv6 Proxies](https://raw.githubusercontent.com/soroushmirzaei/telegram-proxies-collector/main/layers/ipv6)\n"
        first_message += "• [Web Interface](https://soroushmirzaei.github.io/telegram-proxies-collector)\n"
        
        # Send the first message with retry mechanism
        max_retries = MAX_RETRIES
        for attempt in range(max_retries):
            try:
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=first_message,
                    parse_mode='Markdown',
                    disable_web_page_preview=True,
                    read_timeout=REQUEST_TIMEOUT,
                    write_timeout=REQUEST_TIMEOUT,
                    connect_timeout=REQUEST_TIMEOUT
                )
                break
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to send first message: {e}")
                if attempt == max_retries - 1:
                    logger.error("Failed to send first message after all retries")
                    return False
                await asyncio.sleep(2)  # Wait before retrying
        
        # Define a list of emojis
        emojis = ['🌁', '🌃', '🏙️', '🌄', '🌅', '🌇', '🏞️']
        
        # Prepare and send proxy links in batches
        batch_size = 10
        total_batches = (len(proxy_links) + batch_size - 1) // batch_size
        
        for batch in range(total_batches):
            # Calculate start and end indices for this batch
            start_idx = batch * batch_size
            end_idx = min((batch + 1) * batch_size, len(proxy_links))
            batch_links = proxy_links[start_idx:end_idx]
            
            # Prepare batch message
            current_message = f"*Proxy Links ( Page : {batch + 1}):*\n"
            for i, link in enumerate(batch_links, start=1):
                # Calculate global index
                global_index = start_idx + i
                # Select a random emoji
                emoji = random.choice(emojis)
                current_message += f"---------------\n"
                current_message += f"[Proxy {global_index}  {emoji}]({link})\n"
                current_message += f"---------------\n"
            
            # Append the specified text to the end of the message
            current_message += "\n@proxyroohejangali"
            
            # Send batch message with retry mechanism
            for attempt in range(max_retries):
                try:
                    await bot.send_message(
                        chat_id=CHANNEL_ID,
                        text=current_message,
                        parse_mode='Markdown',
                        disable_web_page_preview=True,
                        read_timeout=REQUEST_TIMEOUT,
                        write_timeout=REQUEST_TIMEOUT,
                        connect_timeout=REQUEST_TIMEOUT
                    )
                    break
                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1} failed to send batch {batch + 1}: {e}")
                    if attempt == max_retries - 1:
                        logger.error(f"Failed to send batch {batch + 1} after all retries")
                        return False
                    # Implement exponential backoff
                    await asyncio.sleep(2 ** attempt * 2)  # Wait before retrying
            
            # Add a longer delay between batches to prevent rate limiting
            await asyncio.sleep(5)  # Increase delay to 5 seconds
        
        logger.info(f"Successfully sent proxies to channel {CHANNEL_ID}")
        return True
        
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(send_proxies_to_channel()) 