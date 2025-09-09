#!/usr/bin/env python3
"""
Telegram Trading Bot - Main Entry Point
A sophisticated trading bot for crypto and forex signals with adaptive strategies
"""

import os
import sys
import asyncio
import logging
from threading import Thread
from flask import Flask, jsonify
import signal
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from telegram_handler import TelegramBot
from database import init_database
from data_handler import MarketDataHandler
from strategy import StrategyManager
from reporting import ReportingSystem
from logger import setup_logging

# Setup logging
logger = setup_logging()

# Flask app for health checks (required by Render)
app = Flask(__name__)

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy',
        'service': 'telegram-trading-bot',
        'timestamp': os.environ.get('RENDER_SERVICE_ID', 'local')
    })

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'message': 'Telegram Trading Bot is running',
        'status': 'active'
    })

class TradingBotOrchestrator:
    """Main orchestrator for the trading bot"""
    
    def __init__(self):
        self.telegram_bot = None
        self.market_data = None
        self.strategy_manager = None
        self.reporting = None
        self.running = False
    
    async def initialize(self):
        """Initialize all components"""
        try:
            logger.info("🚀 Initializing Telegram Trading Bot...")
            
            # Initialize database
            await init_database()
            logger.info("✅ Database initialized")
            
            # Initialize components
            self.market_data = MarketDataHandler()
            self.strategy_manager = StrategyManager()
            self.reporting = ReportingSystem()
            self.telegram_bot = TelegramBot(
                market_data=self.market_data,
                strategy_manager=self.strategy_manager,
                reporting=self.reporting
            )
            
            logger.info("✅ All components initialized")
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise
    
    async def start(self):
        """Start the trading bot"""
        try:
            await self.initialize()
            self.running = True
            
            logger.info("🎯 Starting Telegram Trading Bot...")
            
            # Start all components
            await asyncio.gather(
                self.telegram_bot.start(),
                self.strategy_manager.start_monitoring(),
                self.reporting.start_daily_reports(),
                self.market_data.start_data_collection()
            )
            
        except Exception as e:
            logger.error(f"❌ Bot start failed: {e}")
            raise
    
    async def stop(self):
        """Stop the trading bot gracefully"""
        if self.running:
            logger.info("🛑 Stopping Telegram Trading Bot...")
            self.running = False
            
            if self.telegram_bot:
                await self.telegram_bot.stop()
            if self.strategy_manager:
                await self.strategy_manager.stop()
            if self.reporting:
                await self.reporting.stop()
            if self.market_data:
                await self.market_data.stop()
                
            logger.info("✅ Bot stopped gracefully")

def run_flask_app():
    """Run Flask app in a separate thread for health checks"""
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

async def main():
    """Main function"""
    bot_orchestrator = TradingBotOrchestrator()
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        bot_orchestrator.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start Flask server in background thread for health checks
        flask_thread = Thread(target=run_flask_app, daemon=True)
        flask_thread.start()
        logger.info("🌐 Health check server started")
        
        # Start the trading bot with timeout
        try:
            await asyncio.wait_for(bot_orchestrator.start(), timeout=60.0)
        except asyncio.TimeoutError:
            logger.error("Bot startup timed out after 60 seconds")
            raise
        
    except KeyboardInterrupt:
        logger.info("📱 Keyboard interrupt received")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
    finally:
        await bot_orchestrator.stop()

if __name__ == "__main__":
    # Check for required environment variables
    required_env_vars = [
        'TELEGRAM_BOT_TOKEN',
        'DATABASE_URL',
        'ALPHA_VANTAGE_API_KEY'
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        sys.exit(1)
    
    # Run the bot
    asyncio.run(main())
