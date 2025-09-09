"""
Telegram Bot Handler for Trading Signals
"""

import os
import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import html
import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes
)
from telegram.constants import ParseMode

from logger import get_trading_logger
from database import get_db_session, TradingSignal, Trade, UserInteraction

logger = get_trading_logger()

class TelegramBot:
    """Main Telegram bot handler"""
    
    def __init__(self, market_data=None, strategy_manager=None, reporting=None):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")
        
        self.market_data = market_data
        self.strategy_manager = strategy_manager
        self.reporting = reporting
        
        self.application = None
        self.running = False
    
    async def start(self):
        """Start the Telegram bot"""
        try:
            logger.log_system_event("Starting Telegram bot")
            
            # Create application
            self.application = Application.builder().token(self.token).build()
            
            # Add handlers
            await self._setup_handlers()
            
            # Initialize and start
            await self.application.initialize()
            await self.application.start()
            
            # Start polling
            await self.application.updater.start_polling()
            self.running = True
            
            logger.log_system_event("Telegram bot started successfully")
            
            # Send startup message
            if self.chat_id:
                startup_msg = (
                    "🤖 *Trading Bot Started*\n\n"
                    "✅ System initialized\n"
                    "📊 Ready to generate signals\n"
                    "🎯 Target: 50\-80 pips daily\n\n"
                    "Use /help for available commands"
                )
                try:
                    await self.application.bot.send_message(
                        chat_id=self.chat_id,
                        text=startup_msg,
                        parse_mode=ParseMode.MARKDOWN_V2
                    )
                    logger.log_system_event("Startup message sent successfully")
                except Exception as e:
                    logger.log_error(e, {"context": "startup_message"})
            
            # Keep running
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.log_error(e, {"context": "telegram_bot_start"})
            raise
    
    async def stop(self):
        """Stop the Telegram bot"""
        if self.running and self.application:
            logger.log_system_event("Stopping Telegram bot")
            
            self.running = False
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            
            logger.log_system_event("Telegram bot stopped")
    
    async def _setup_handlers(self):
        """Setup all command and callback handlers"""
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self._cmd_start))
        self.application.add_handler(CommandHandler("help", self._cmd_help))
        self.application.add_handler(CommandHandler("status", self._cmd_status))
        self.application.add_handler(CommandHandler("performance", self._cmd_performance))
        self.application.add_handler(CommandHandler("signals", self._cmd_signals))
        self.application.add_handler(CommandHandler("trades", self._cmd_trades))
        self.application.add_handler(CommandHandler("settings", self._cmd_settings))
        self.application.add_handler(CommandHandler("generate", self._cmd_generate_signal))
        
        # Callback query handler for inline keyboards
        self.application.add_handler(CallbackQueryHandler(self._handle_callback))
        
        # Message handler for text messages
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message)
        )
        
        logger.log_system_event("Telegram bot handlers setup complete")
    
    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await self._log_interaction(update, "start_command")
        
        welcome_message = (
            "🎯 **Welcome to Trading Signal Bot**\\n\\n"
            "This bot provides professional trading signals for:\\n"
            "• 💱 Major Forex pairs\\n"
            "• 🏆 Gold (XAUUSD)\\n"  
            "• ₿ Major cryptocurrencies\\n\\n"
            "**Target:** 50-80 pips daily profit\\n"
            "**Strategy:** Multi-confluence technical analysis\\n"
            "**Features:** Adaptive learning & performance tracking\\n\\n"
            "Use /help to see all available commands"
        )
        
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN_V2
        )
    
    async def _cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        await self._log_interaction(update, "help_command")
        
        help_message = (
            "🤖 **Available Commands**\\n\\n"
            "📊 **Trading & Signals**\\n"
            "• `/signals` - View recent signals\\n"
            "• `/trades` - View trade history\\n"
            "• `/performance` - Performance metrics\\n\\n"
            "⚙️ **Bot Management**\\n"  
            "• `/status` - Bot status & health\\n"
            "• `/settings` - Bot configuration\\n\\n"
            "🔄 **Reports**\\n"
            "• Daily reports sent automatically at 8:00 UTC\\n"
            "• Weekly reports sent on Sundays\\n"
            "• `/generate` \- Force generate signal (if in trading session)\\n\\n"
            "🕰 **Trading Sessions:**\\n"
            "• London: 08:00\-17:00 UTC\\n"
            "• New York: 13:00\-22:00 UTC\\n"
            "• Best: 13:00\-17:00 UTC \(Overlap\)"
        )
        
        await update.message.reply_text(
            help_message,
            parse_mode=ParseMode.MARKDOWN_V2
        )
    
    async def _cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        await self._log_interaction(update, "status_command")
        
        # Get system status
        status_data = await self._get_system_status()
        
        status_message = (
            f"🤖 **Bot Status**\\n\\n"
            f"🟢 **System:** {status_data['system_status']}\\n"
            f"📊 **Data Feed:** {status_data['data_feed_status']}\\n"
            f"🎯 **Strategy:** {status_data['active_strategy']}\\n"
            f"📈 **Signals Today:** {status_data['signals_today']}\\n"
            f"💰 **Daily P&L:** {status_data['daily_pnl']:+.1f} pips\\n"
            f"📅 **Last Signal:** {status_data['last_signal_time']}\\n\\n"
            f"⏰ **Uptime:** {status_data['uptime']}"
        )
        
        await update.message.reply_text(
            status_message,
            parse_mode=ParseMode.MARKDOWN_V2
        )
    
    async def _cmd_performance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /performance command"""
        await self._log_interaction(update, "performance_command")
        
        performance_message = (
            "📊 *Performance Summary*\n\n"
            "*Today:*\n"
            "• Signals: 0\n"
            "• Trades: 0\n"
            "• P&L: +0.0 pips\n\n"
            "*This Week:*\n"
            "• Signals: 0\n"
            "• Win Rate: 0.0%\n"
            "• Total P&L: +0.0 pips\n\n"
            "*Trading Sessions:*\n"
            "• London: 08:00-17:00 UTC\n"
            "• New York: 13:00-22:00 UTC\n"
            "• Best Time: 13:00-17:00 UTC (Overlap)"
        )
        
        await update.message.reply_text(
            performance_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def _cmd_generate_signal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /generate command - Force generate a signal"""
        await self._log_interaction(update, "generate_signal_command")
        
        if not self.strategy_manager:
            await update.message.reply_text(
                "❌ Strategy manager not available",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Check if in trading session
        if not self.strategy_manager.is_trading_session_active():
            from datetime import datetime, timezone
            current_hour = datetime.now(timezone.utc).hour
            
            next_london = "08:00 UTC" if current_hour < 8 else "08:00 UTC tomorrow"
            next_ny = "13:00 UTC" if current_hour < 13 else "13:00 UTC tomorrow"
            
            await update.message.reply_text(
                f"🚫 *Not in active trading session*\n\n"
                f"Current time: {current_hour:02d}:XX UTC\n\n"
                f"*Next sessions:*\n"
                f"• London: {next_london}\n"
                f"• New York: {next_ny}\n\n"
                f"Signals are only generated during:\n"
                f"• London: 08:00-17:00 UTC\n"
                f"• New York: 13:00-22:00 UTC",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Try to generate signal
        try:
            market_data = {'current_price': 1.0950}  # Demo data
            signal = await self.strategy_manager.generate_signal('EURUSD', market_data)
            
            if signal:
                signal_message = (
                    f"🚨 *TRADING SIGNAL*\n\n"
                    f"*Pair:* {signal['symbol']}\n"
                    f"*Direction:* {signal['type']}\n"
                    f"*Entry:* {signal['entry_price']:.5f}\n"
                    f"*Stop Loss:* {signal['stop_loss']:.5f}\n"
                    f"*Take Profit:* {signal['take_profit']:.5f}\n"
                    f"*Confluence:* {signal['confluence_score']:.1f}%\n"
                    f"*Session:* {signal['session']}\n\n"
                    f"📈 *Risk:Reward Ratio:* 1:2.5\n"
                    f"⚙️ *Strategy:* {signal['strategy']}"
                )
                
                await update.message.reply_text(
                    signal_message,
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text(
                    f"🚫 *No signal generated*\n\n"
                    f"Reasons could be:\n"
                    f"• Daily limit reached (3 signals)\n"
                    f"• Market conditions not favorable\n"
                    f"• Confluence score below 70%\n\n"
                    f"Signals: {self.strategy_manager.signals_today}/3 today",
                    parse_mode=ParseMode.MARKDOWN
                )
                
        except Exception as e:
            logger.log_error(e, {"context": "manual_signal_generation"})
            await update.message.reply_text(
                "❌ Error generating signal. Please try again later.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def _cmd_signals(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /signals command"""
        await self._log_interaction(update, "signals_command")
        
        # Get recent signals from database
        async with get_db_session() as session:
            # Implementation would fetch recent signals
            signals_message = (
                "📡 **Recent Signals**\\n\\n"
                "🔍 No recent signals found\\n"
                "Next analysis in progress\\.\\.\\."
            )
        
        await update.message.reply_text(
            signals_message,
            parse_mode=ParseMode.MARKDOWN_V2
        )
    
    async def _cmd_trades(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /trades command"""
        await self._log_interaction(update, "trades_command")
        
        # Implementation would fetch recent trades
        trades_message = (
            "💼 **Recent Trades**\\n\\n"
            "No recent trades to display"
        )
        
        await update.message.reply_text(
            trades_message,
            parse_mode=ParseMode.MARKDOWN_V2
        )
    
    async def _cmd_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command"""
        await self._log_interaction(update, "settings_command")
        
        keyboard = [
            [InlineKeyboardButton("🔔 Notifications", callback_data="settings_notifications")],
            [InlineKeyboardButton("📊 Risk Management", callback_data="settings_risk")],
            [InlineKeyboardButton("🎯 Target Pairs", callback_data="settings_pairs")],
            [InlineKeyboardButton("📈 Strategy", callback_data="settings_strategy")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚙️ **Bot Settings**\\n\\nSelect a category to configure:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2
        )
    
    async def _handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()
        
        await self._log_interaction(update, "callback_query", {"data": query.data})
        
        if query.data.startswith("settings_"):
            setting_type = query.data.replace("settings_", "")
            await self._handle_settings_callback(query, setting_type)
        elif query.data.startswith("trade_"):
            await self._handle_trade_callback(query, query.data)
    
    async def _handle_settings_callback(self, query, setting_type: str):
        """Handle settings-related callbacks"""
        settings_info = {
            "notifications": "🔔 Notifications are currently enabled\\nDaily reports: 8:00 UTC\\nWeekly reports: Sunday 10:00 UTC",
            "risk": "📊 Current Risk Settings\\nMax risk per trade: 2%\\nDaily trade limit: 3\\nStop loss: 30 pips",
            "pairs": "🎯 Monitored Pairs\\nForex: EURUSD, GBPUSD, USDJPY\\nCommodity: XAUUSD\\nCrypto: BTCUSDT, ETHUSDT",
            "strategy": "📈 Active Strategy: Multi-Confluence\\nAdaptive learning enabled\\nConfluence threshold: 70%"
        }
        
        await query.edit_message_text(
            f"⚙️ **Settings**\\n\\n{settings_info.get(setting_type, 'Setting not found')}",
            parse_mode=ParseMode.MARKDOWN_V2
        )
    
    async def _handle_trade_callback(self, query, callback_data: str):
        """Handle trade-related callbacks"""
        # Implementation for trade confirmations, etc.
        await query.edit_message_text("Trade callback handled")
    
    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        await self._log_interaction(update, "text_message", {"text": update.message.text})
        
        # Simple response for now
        await update.message.reply_text(
            "I received your message\\. Use /help to see available commands\\.",
            parse_mode=ParseMode.MARKDOWN_V2
        )
    
    async def send_signal(self, signal_data: Dict[str, Any]):
        """Send a trading signal to the user"""
        if not self.chat_id:
            logger.log_system_event("No chat ID configured for sending signals")
            return
        
        try:
            # Format signal message
            signal_message = self._format_signal_message(signal_data)
            
            # Create inline keyboard for trade confirmation
            keyboard = [
                [
                    InlineKeyboardButton("✅ Trade Taken", callback_data=f"trade_taken_{signal_data['id']}"),
                    InlineKeyboardButton("❌ Trade Skipped", callback_data=f"trade_skipped_{signal_data['id']}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send signal
            await self.application.bot.send_message(
                chat_id=self.chat_id,
                text=signal_message,
                parse_mode=ParseMode.MARKDOWN_V2,
                reply_markup=reply_markup
            )
            
            logger.log_signal(
                signal_data['symbol'],
                signal_data['type'],
                signal_data
            )
            
        except Exception as e:
            logger.log_error(e, {"context": "send_signal", "signal": signal_data})
    
    async def send_message(self, message: str):
        """Send a general message to the user"""
        if not self.chat_id:
            return
        
        try:
            await self.application.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN_V2
            )
        except Exception as e:
            logger.log_error(e, {"context": "send_message"})
    
    def _format_signal_message(self, signal_data: Dict[str, Any]) -> str:
        """Format a trading signal message"""
        symbol = signal_data['symbol']
        signal_type = signal_data['type']
        entry = signal_data['entry_price']
        sl = signal_data['stop_loss']
        tp = signal_data['take_profit']
        confluence = signal_data['confluence_score']
        
        # Calculate pips potential
        if signal_type == "BUY":
            pips_potential = tp - entry
        else:
            pips_potential = entry - tp
        
        # Format message
        message = (
            f"🎯 **TRADING SIGNAL**\\n\\n"
            f"📊 **Pair:** {symbol}\\n"
            f"📈 **Direction:** {signal_type}\\n"
            f"💰 **Entry:** {entry:.5f}\\n"
            f"🛑 **Stop Loss:** {sl:.5f}\\n"
            f"🎯 **Take Profit:** {tp:.5f}\\n\\n"
            f"📊 **Confluence Score:** {confluence:.1f}%\\n"
            f"💎 **Pips Potential:** {pips_potential*10000:.0f} pips\\n\\n"
            f"⏰ **Time:** {datetime.now(timezone.utc).strftime('%H:%M UTC')}\\n\\n"
            f"Did you take this trade?"
        )
        
        return message
    
    async def _log_interaction(self, update: Update, interaction_type: str, context_data: Dict = None):
        """Log user interaction to database"""
        try:
            user_id = str(update.effective_user.id)
            
            async with get_db_session() as session:
                interaction = UserInteraction(
                    user_id=user_id,
                    interaction_type=interaction_type,
                    command=getattr(update.message, 'text', None) if update.message else None,
                    context_data=context_data or {}
                )
                session.add(interaction)
                await session.commit()
                
        except Exception as e:
            logger.log_error(e, {"context": "log_interaction"})
    
    async def _get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        # This would be implemented with actual system checks
        return {
            "system_status": "Online",
            "data_feed_status": "Connected",
            "active_strategy": "Multi-Confluence", 
            "signals_today": 0,
            "daily_pnl": 0.0,
            "last_signal_time": "No signals today",
            "uptime": "Just started"
        }

def verify_bot_token() -> bool:
    """Verify that the bot token is valid"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        return False
    
    # Basic validation - actual implementation would test the token
    return len(token) > 20 and ':' in token
