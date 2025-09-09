#!/usr/bin/env python3
"""
Simplified Telegram Trading Bot - For Testing
"""

import os
import sys
import asyncio
import signal
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from telegram import Bot
from logger import setup_logging

# Setup logging
logger = setup_logging()

async def main():
    """Simple bot startup"""
    
    # Get credentials
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        logger.error("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        return
    
    try:
        # Create bot
        bot = Bot(token=token)
        logger.info("🤖 Bot created successfully")
        
        # Test connection
        me = await bot.get_me()
        logger.info(f"✅ Connected as @{me.username}")
        
        # Send startup message
        startup_msg = (
            "🚀 *Trading Bot Started*\n\n"
            "✅ System initialized\n"
            "📊 Ready to generate signals\n"
            "🎯 Target: 50-80 pips daily\n\n"
            "Commands:\n"
            "/start - Welcome message\n"
            "/help - List all commands\n"
            "/status - Bot status\n"
            "/performance - Performance metrics"
        )
        
        await bot.send_message(
            chat_id=chat_id,
            text=startup_msg,
            parse_mode='Markdown'
        )
        
        logger.info("✅ Startup message sent!")
        logger.info("🎯 Bot is ready. Try /start in Telegram!")
        
        # Keep running
        print("\n🤖 Bot is running. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
