"""
Database models and ORM setup for the Telegram Trading Bot
"""

import os
import asyncio
from datetime import datetime, timezone
from typing import Optional, List
from decimal import Decimal

import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import (
    String, Integer, Float, DateTime, Boolean, Text, 
    ForeignKey, Index, UniqueConstraint, JSON
)
from sqlalchemy.dialects.postgresql import UUID
import uuid

from logger import get_trading_logger

logger = get_trading_logger()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+asyncpg://', 1)
    elif DATABASE_URL.startswith('postgresql://') and '+asyncpg' not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://', 1)

class Base(DeclarativeBase):
    """Base class for all database models"""
    pass

# Database engine and session factory
engine = None
async_session_factory = None

async def init_database():
    """Initialize database connection and create tables"""
    global engine, async_session_factory
    
    try:
        logger.log_system_event("Initializing database connection")
        
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Create async engine
        engine = create_async_engine(
            DATABASE_URL,
            echo=False,  # Set to True for SQL debugging
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=1800,  # 30 minutes
        )
        
        # Create session factory
        async_session_factory = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.log_system_event("Database initialized successfully")
        
    except Exception as e:
        logger.log_error(e, {"context": "database_initialization"})
        raise

async def get_db_session() -> AsyncSession:
    """Get a database session"""
    if async_session_factory is None:
        await init_database()
    
    return async_session_factory()

class TradingSignal(Base):
    """Model for storing trading signals"""
    __tablename__ = "trading_signals"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    signal_type: Mapped[str] = mapped_column(String(10), nullable=False)  # BUY/SELL
    strategy_name: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Price levels
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    stop_loss: Mapped[float] = mapped_column(Float, nullable=False)
    take_profit: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Signal quality metrics
    confluence_score: Mapped[float] = mapped_column(Float, nullable=False)
    strength: Mapped[str] = mapped_column(String(10), nullable=False)  # WEAK/MEDIUM/STRONG
    
    # Timing
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Status tracking
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")  # ACTIVE/EXECUTED/EXPIRED/CANCELLED
    sent_to_telegram: Mapped[bool] = mapped_column(Boolean, default=False)
    is_secondary_signal: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Additional data
    indicators_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    trades: Mapped[List["Trade"]] = relationship("Trade", back_populates="signal")
    
    # Indexes
    __table_args__ = (
        Index('idx_trading_signals_symbol', 'symbol'),
        Index('idx_trading_signals_created_at', 'created_at'),
        Index('idx_trading_signals_status', 'status'),
    )

class Trade(Base):
    """Model for storing executed trades"""
    __tablename__ = "trades"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    signal_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey('trading_signals.id'), nullable=True)
    
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    trade_type: Mapped[str] = mapped_column(String(10), nullable=False)  # BUY/SELL
    
    # Trade execution details
    entry_price: Mapped[float] = mapped_column(Float, nullable=False)
    exit_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Risk management
    stop_loss: Mapped[float] = mapped_column(Float, nullable=False)
    take_profit: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Trade outcomes
    pips_gained: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pnl: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    commission: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    
    # Timing
    entered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    exited_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Status and outcome
    status: Mapped[str] = mapped_column(String(20), default="OPEN")  # OPEN/CLOSED/STOPPED
    outcome: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # WIN/LOSS/BREAKEVEN
    
    # User interaction
    user_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    confirmation_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    signal: Mapped[Optional[TradingSignal]] = relationship("TradingSignal", back_populates="trades")
    
    # Indexes
    __table_args__ = (
        Index('idx_trades_symbol', 'symbol'),
        Index('idx_trades_entered_at', 'entered_at'),
        Index('idx_trades_status', 'status'),
    )

class StrategyPerformance(Base):
    """Model for tracking strategy performance metrics"""
    __tablename__ = "strategy_performance"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    strategy_name: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Time period
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_type: Mapped[str] = mapped_column(String(10), nullable=False)  # DAILY/WEEKLY/MONTHLY
    
    # Performance metrics
    signals_generated: Mapped[int] = mapped_column(Integer, default=0)
    trades_executed: Mapped[int] = mapped_column(Integer, default=0)
    trades_won: Mapped[int] = mapped_column(Integer, default=0)
    trades_lost: Mapped[int] = mapped_column(Integer, default=0)
    
    total_pips: Mapped[float] = mapped_column(Float, default=0.0)
    total_pnl: Mapped[float] = mapped_column(Float, default=0.0)
    win_rate: Mapped[float] = mapped_column(Float, default=0.0)
    avg_risk_reward: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Strategy specific metrics
    avg_confluence_score: Mapped[float] = mapped_column(Float, default=0.0)
    max_drawdown: Mapped[float] = mapped_column(Float, default=0.0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Indexes
    __table_args__ = (
        Index('idx_strategy_performance_name_date', 'strategy_name', 'date'),
        Index('idx_strategy_performance_period', 'period_type'),
        UniqueConstraint('strategy_name', 'date', 'period_type', name='uq_strategy_performance'),
    )

class SystemEvent(Base):
    """Model for tracking system events and adaptations"""
    __tablename__ = "system_events"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Event details
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(10), default="INFO")  # INFO/WARNING/ERROR/CRITICAL
    
    # Context data
    context_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timing
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")  # ACTIVE/RESOLVED/ACKNOWLEDGED
    
    # Indexes
    __table_args__ = (
        Index('idx_system_events_type', 'event_type'),
        Index('idx_system_events_occurred_at', 'occurred_at'),
        Index('idx_system_events_severity', 'severity'),
    )

class MarketData(Base):
    """Model for storing historical market data"""
    __tablename__ = "market_data"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(5), nullable=False)  # 1m, 5m, 15m, 1h, 4h, 1d
    
    # OHLCV data
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    open_price: Mapped[float] = mapped_column(Float, nullable=False)
    high_price: Mapped[float] = mapped_column(Float, nullable=False)
    low_price: Mapped[float] = mapped_column(Float, nullable=False)
    close_price: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Technical indicators (computed and cached)
    rsi: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    macd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    macd_signal: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bb_upper: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bb_lower: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Indexes
    __table_args__ = (
        Index('idx_market_data_symbol_timeframe', 'symbol', 'timeframe'),
        Index('idx_market_data_timestamp', 'timestamp'),
        UniqueConstraint('symbol', 'timeframe', 'timestamp', name='uq_market_data'),
    )

class UserInteraction(Base):
    """Model for tracking user interactions with the bot"""
    __tablename__ = "user_interactions"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(50), nullable=False)
    interaction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Interaction details
    command: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Context
    context_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    # Timing
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Indexes
    __table_args__ = (
        Index('idx_user_interactions_user_id', 'user_id'),
        Index('idx_user_interactions_type', 'interaction_type'),
        Index('idx_user_interactions_occurred_at', 'occurred_at'),
    )
