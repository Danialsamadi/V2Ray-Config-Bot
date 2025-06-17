#!/usr/bin/env python3
"""
Placeholder for future Telegram bot interactive functionality.
Currently, the bot functionality is handled by bot.py for channel posting.
"""

import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO'))
)
logger = logging.getLogger(__name__)

# Load environment variables
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def start(update, context):
    """Handler for the /start command."""
    await update.message.reply_text(
        "Welcome to V2Ray-Config-Bot! "
        "This bot helps you discover and manage V2Ray proxy configurations."
    )

async def help_command(update, context):
    """Handler for the /help command."""
    help_text = """
Available commands:
/start - Start the bot
/help - Show this help message
/proxies - Get latest proxy list
    """
    await update.message.reply_text(help_text)

async def get_proxies(update, context):
    """Retrieve and send latest proxies."""
    try:
        with open('./proxies', 'r') as f:
            proxies = f.read()
        
        # Limit message length
        if len(proxies) > 4000:
            proxies = proxies[:4000] + "... (truncated)"
        
        await update.message.reply_text(f"Latest Proxies:\n```\n{proxies}\n```", parse_mode='Markdown')
    except FileNotFoundError:
        await update.message.reply_text("No proxies found. Run the collection script first.")
    except Exception as e:
        logger.error(f"Error retrieving proxies: {e}")
        await update.message.reply_text("An error occurred while retrieving proxies.")

def main():
    """Main function to start the Telegram bot."""
    if not BOT_TOKEN:
        logger.error("No bot token provided. Set TELEGRAM_BOT_TOKEN environment variable.")
        return

    # Create the Application and pass it your bot's token
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("proxies", get_proxies))

    # Start the bot
    logger.info("Starting V2Ray-Config-Bot...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main() 