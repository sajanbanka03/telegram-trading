#!/usr/bin/env python3
"""
Quick test script for Telegram Trading Bot
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def test_components():
    """Test individual components before full bot startup"""
    
    print("🔧 Testing bot components...")
    
    # Test environment variables
    required_vars = ['TELEGRAM_BOT_TOKEN', 'DATABASE_URL', 'ALPHA_VANTAGE_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False
    else:
        print("✅ All required environment variables present")
    
    # Test database connection
    try:
        from database import init_database
        await init_database()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Test Telegram bot token
    try:
        from telegram_handler import TelegramBot
        bot = TelegramBot()
        print("✅ Telegram bot initialized")
    except Exception as e:
        print(f"❌ Telegram bot initialization failed: {e}")
        return False
    
    print("✅ All components working! Bot should start successfully.")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_components())
    if success:
        print("\n🚀 Run: python bot.py")
        print("\n📱 Telegram Commands to test:")
        print("   /start - Welcome message")
        print("   /help - Available commands") 
        print("   /status - Bot status")
        print("   /performance - Performance metrics")
    else:
        print("\n❌ Fix the issues above before running the bot")
