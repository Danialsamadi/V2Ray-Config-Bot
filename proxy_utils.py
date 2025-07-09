import os
import logging
from datetime import datetime, timezone, timedelta
import pytz
import urllib.parse
import random
from telegram import Bot
import asyncio
from dotenv import load_dotenv
import jdatetime

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))
BATCH_SIZE = 10

logger = logging.getLogger(__name__)

def save_proxies(proxies, filename=None):
    # Only save to proxies.txt (one per line, no header)
    with open('proxies.txt', 'w') as f:
        for proxy in proxies:
            if proxy.startswith('https://t.me/proxy?'):
                proxy = 'tg://proxy?' + proxy.split('?', 1)[1]
            f.write(f"{proxy}\n")
    logger.info(f"Saved {len(proxies)} proxies to proxies.txt")

async def send_proxies_to_channel(proxies):
    if not BOT_TOKEN or not CHANNEL_ID:
        logger.error("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHANNEL_ID.")
        return False
    # Randomly sample up to 1000 proxies
    if len(proxies) > 1000:
        proxies = random.sample(proxies, 1000)
    bot = Bot(token=BOT_TOKEN)
    tehran_tz = pytz.timezone('Asia/Tehran')
    current_datetime = datetime.now(tehran_tz)
    datetime_str = current_datetime.strftime("%a, %d %b %Y %H:%M:%S")
    # Add Jalali (Persian) date string
    jalali_datetime = jdatetime.datetime.fromgregorian(datetime=current_datetime)
    jalali_str = jalali_datetime.strftime("%A، %d %B %Y %H:%M:%S")
    # Bilingual summary message
    first_message = (
        f"<b>🔄 آخرین بروزرسانی پروکسی‌ها:</b> {jalali_str}\n\n"
        f"<b>📄 تعداد کل پروکسی‌های جمع آوری شده:</b> {len(proxies)}\n\n"
        f"<blockquote>⚠️ بسته به ویژگی‌ها و کیفیت اتصال اینترنت و نسخه کلاینت تلگرام شما، برخی سرورهای پروکسی ممکن است عملکرد مطلوبی نداشته باشند. بنابراین، پیشنهاد می‌شود پروکسی‌های جایگزین را آزمایش کرده و از گزینه‌هایی استفاده کنید که سازگاری و کارایی بهتری ارائه می‌دهند. ⚠️</blockquote>\n\n"
        f"<a href='https://telegra.ph/Terms-and-Conditions-07-08-3'>شرایط و قوانین</a> | <a href='https://telegra.ph/FAQ---Frequently-Asked-Question-07-09'>سوالات متداول</a>\n\n"
        f"<b>🔄 Latest Proxies Update:</b> {datetime_str}\n\n"
        f"<b>📄 Total Proxies Collected:</b> {len(proxies)}\n\n"
        f"<blockquote>⚠️ Depending on the characteristics and quality of your internet connection and the version of your Telegram client, some proxy servers may not perform optimally. Therefore, it is recommended to test alternative proxies and use those that offer better compatibility and efficiency. ⚠️</blockquote>\n\n"
        f"<a href='https://telegra.ph/Terms-and-Conditions-07-08-3'>Terms and Conditions</a> | <a href='https://telegra.ph/FAQ---Frequently-Asked-Question-07-09'>FAQ - Frequently Asked Questions</a>\n\n"
        f"@proxyroohejangali"
    )
    summary_message = None
    for attempt in range(MAX_RETRIES):
        try:
            summary_message = await bot.send_message(
                chat_id=CHANNEL_ID,
                text=first_message,
                parse_mode='HTML',
                disable_web_page_preview=True,
                read_timeout=REQUEST_TIMEOUT,
                write_timeout=REQUEST_TIMEOUT,
                connect_timeout=REQUEST_TIMEOUT
            )
            await bot.pin_chat_message(chat_id=CHANNEL_ID, message_id=summary_message.message_id, disable_notification=True)
            break
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed to send summary: {e}")
            if attempt == MAX_RETRIES - 1:
                logger.error("Failed to send summary after all retries")
                return False
            await asyncio.sleep(2)
    emojis = ['🌁', '🌃', '🏙️', '🌄', '🌅', '🌇', '🏞️']
    total_batches = (len(proxies) + BATCH_SIZE - 1) // BATCH_SIZE
    for batch in range(total_batches):
        start_idx = batch * BATCH_SIZE
        end_idx = min((batch + 1) * BATCH_SIZE, len(proxies))
        batch_links = proxies[start_idx:end_idx]
        current_message = f"*Proxy Links (Page {batch + 1}):*\n"
        for i, link in enumerate(batch_links, start=1):
            emoji = random.choice(emojis)
            safe_link = urllib.parse.quote(link, safe=':/?&=')
            current_message += f"---------------\n[Proxy {start_idx + i}  {emoji}]({safe_link})\n---------------\n"
        current_message += "\n@proxyroohejangali"
        for attempt in range(MAX_RETRIES):
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
                if attempt == MAX_RETRIES - 1:
                    logger.error(f"Failed to send batch {batch + 1} after all retries")
                    return False
                await asyncio.sleep(2 ** attempt * 2)
        await asyncio.sleep(5)
    logger.info(f"Successfully sent proxies to channel {CHANNEL_ID}")
    return True