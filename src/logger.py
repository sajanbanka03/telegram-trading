"""
Comprehensive logging system for the Telegram Trading Bot
"""

import os
import sys
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
import structlog
from typing import Optional


def setup_logging(
    log_level: Optional[str] = None,
    log_dir: str = "logs"
) -> structlog.BoundLogger:
    """Setup comprehensive logging configuration"""
    
    # Create logs directory if it doesn't exist
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Determine log level
    if log_level is None:
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Configure standard logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler with rotation
            logging.handlers.RotatingFileHandler(
                filename=os.path.join(log_dir, 'bot.log'),
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
        ]
    )
    
    # Configure structured logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Create specialized loggers
    setup_trade_logger(log_dir)
    setup_error_logger(log_dir)
    
    # Return main logger
    logger = structlog.get_logger("telegram_trading_bot")
    logger.info("Logging system initialized", log_level=log_level, log_dir=log_dir)
    
    return logger


def setup_trade_logger(log_dir: str) -> None:
    """Setup specialized logger for trade-related events"""
    trade_logger = logging.getLogger('trades')
    trade_logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplication
    trade_logger.handlers.clear()
    
    # Add file handler for trades
    trade_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, 'trades.log'),
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=10,
        encoding='utf-8'
    )
    
    trade_formatter = logging.Formatter(
        '%(asctime)s - TRADE - %(levelname)s - %(message)s'
    )
    trade_handler.setFormatter(trade_formatter)
    trade_logger.addHandler(trade_handler)
    
    # Prevent propagation to root logger
    trade_logger.propagate = False


def setup_error_logger(log_dir: str) -> None:
    """Setup specialized logger for errors and exceptions"""
    error_logger = logging.getLogger('errors')
    error_logger.setLevel(logging.ERROR)
    
    # Remove existing handlers to avoid duplication
    error_logger.handlers.clear()
    
    # Add file handler for errors
    error_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, 'errors.log'),
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=10,
        encoding='utf-8'
    )
    
    error_formatter = logging.Formatter(
        '%(asctime)s - ERROR - %(name)s - %(levelname)s - %(message)s\n'
        'Exception: %(exc_info)s\n'
        '%(pathname)s:%(lineno)d in %(funcName)s\n'
        '----------------------------------------'
    )
    error_handler.setFormatter(error_formatter)
    error_logger.addHandler(error_handler)
    
    # Prevent propagation to root logger
    error_logger.propagate = False


class TradingLogger:
    """Specialized logger for trading operations"""
    
    def __init__(self):
        self.main_logger = structlog.get_logger("telegram_trading_bot")
        self.trade_logger = logging.getLogger('trades')
        self.error_logger = logging.getLogger('errors')
    
    def log_signal(self, symbol: str, signal_type: str, details: dict):
        """Log trading signal generation"""
        self.trade_logger.info(
            f"SIGNAL_GENERATED - {symbol} - {signal_type}",
            extra={
                'symbol': symbol,
                'signal_type': signal_type,
                'details': details,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        self.main_logger.info(
            "Trading signal generated",
            symbol=symbol,
            signal_type=signal_type,
            confluence_score=details.get('confluence_score', 0),
            entry_price=details.get('entry_price'),
            stop_loss=details.get('stop_loss'),
            take_profit=details.get('take_profit')
        )
    
    def log_trade_execution(self, symbol: str, action: str, details: dict):
        """Log trade execution"""
        self.trade_logger.info(
            f"TRADE_EXECUTED - {symbol} - {action}",
            extra={
                'symbol': symbol,
                'action': action,
                'details': details,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        self.main_logger.info(
            "Trade executed",
            symbol=symbol,
            action=action,
            price=details.get('price'),
            quantity=details.get('quantity'),
            pnl=details.get('pnl')
        )
    
    def log_strategy_adaptation(self, old_strategy: str, new_strategy: str, reason: str):
        """Log strategy adaptation events"""
        self.trade_logger.warning(
            f"STRATEGY_ADAPTED - {old_strategy} -> {new_strategy}",
            extra={
                'old_strategy': old_strategy,
                'new_strategy': new_strategy,
                'reason': reason,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        self.main_logger.warning(
            "Strategy adapted",
            old_strategy=old_strategy,
            new_strategy=new_strategy,
            reason=reason
        )
    
    def log_performance(self, metrics: dict):
        """Log performance metrics"""
        self.trade_logger.info(
            "PERFORMANCE_UPDATE",
            extra={
                'metrics': metrics,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
        
        self.main_logger.info(
            "Performance metrics updated",
            **metrics
        )
    
    def log_error(self, error: Exception, context: dict = None):
        """Log errors with context"""
        context = context or {}
        
        self.error_logger.error(
            f"Error occurred: {str(error)}",
            extra={
                'error_type': type(error).__name__,
                'error_message': str(error),
                'context': context,
                'timestamp': datetime.utcnow().isoformat()
            },
            exc_info=True
        )
        
        self.main_logger.error(
            "Error occurred",
            error_type=type(error).__name__,
            error_message=str(error),
            **context
        )
    
    def log_system_event(self, event: str, details: dict = None):
        """Log system-level events"""
        details = details or {}
        
        self.main_logger.info(
            event,
            **details
        )


# Global trading logger instance
trading_logger = None

def get_trading_logger() -> TradingLogger:
    """Get the global trading logger instance"""
    global trading_logger
    if trading_logger is None:
        trading_logger = TradingLogger()
    return trading_logger
