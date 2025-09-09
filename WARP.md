# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a sophisticated Python-based Telegram trading bot that provides forex and cryptocurrency trading signals using adaptive machine learning strategies. The bot targets 50-80 pips daily profit with multi-confluence technical analysis and comprehensive performance tracking.

## Architecture

The bot follows a modular, event-driven architecture with these core components:

- **bot.py**: Main orchestrator that coordinates all components and provides health check endpoints for Render deployment
- **src/telegram_handler.py**: Telegram bot interface with command handlers and message processing
- **src/strategy.py**: Trading strategy manager with adaptive learning capabilities
- **src/data_handler.py**: Market data collection from multiple sources (Alpha Vantage, Bybit, OANDA)
- **src/database.py**: Database models and connection management using SQLAlchemy with PostgreSQL
- **src/reporting.py**: Performance tracking and report generation system
- **src/logger.py**: Structured logging system with separate logs for trades, errors, and system events

The system uses asyncio for concurrent processing and supports multiple trading strategies with weighted indicators including RSI, MACD, Bollinger Bands, support/resistance, Fibonacci retracements, and volume analysis.

## Development Commands

### Environment Setup
```bash
# Create environment file from template
cp .env.template .env
# Edit .env with your API keys and configuration

# Install dependencies
pip install -r requirements.txt
```

### Running the Bot
```bash
# Start the bot locally
python bot.py

# The bot requires these environment variables:
# - TELEGRAM_BOT_TOKEN
# - DATABASE_URL  
# - ALPHA_VANTAGE_API_KEY
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_strategy.py

# Run tests with asyncio support
pytest -v tests/ --asyncio-mode=auto
```

### Code Quality
```bash
# Format code with Black
black .

# Lint with flake8
flake8 src/

# Type checking with mypy
mypy src/
```

### Database Operations
```bash
# Initialize database (run automatically on startup)
python -c "
import sys
sys.path.append('src')
from database import init_database
init_database()
"

# The bot uses PostgreSQL with SQLAlchemy async support
# Tables: TradingSignal, Trade, UserInteraction, plus others
```

### Deployment
```bash
# Deploy to Render using the deployment script
./deployment/deploy.sh

# Or deploy via Render's one-click deploy button in README
```

### Monitoring and Logs
```bash
# View main application logs
tail -f logs/bot.log

# View trading-specific logs  
tail -f logs/trades.log

# View error logs
tail -f logs/errors.log

# Health check endpoint (when running)
curl http://localhost:8080/health
```

## Configuration

### Main Configuration
The primary configuration is in `config/config.yaml` with sections for:
- Trading parameters (risk management, target pips, signal generation)
- Strategy configuration (indicator weights, adaptation settings)
- Market data sources and intervals
- Telegram bot behavior and timing
- Reporting metrics and schedules
- Database and logging settings

### Environment Variables
Key environment variables (see `.env.template` for complete list):
- `TELEGRAM_BOT_TOKEN`: Required - Telegram bot token from @BotFather
- `DATABASE_URL`: Required - PostgreSQL connection string
- `ALPHA_VANTAGE_API_KEY`: Required - Primary market data source
- `BYBIT_API_KEY/SECRET_KEY`: Optional - For crypto data
- `OANDA_API_KEY/ACCOUNT_ID`: Optional - For forex data
- `ENVIRONMENT`: development/production
- `TRADING_MODE`: paper/live trading mode

## Key Features and Behavior

### Signal Generation
- Multi-confluence analysis with minimum 70% score required
- Supports major forex pairs, gold (XAUUSD), and major cryptocurrencies
- Adaptive strategy switching after 3 consecutive days without signals
- Secondary signals sent 4 hours after primary if not taken

### Risk Management
- Maximum 2% risk per trade
- Built-in stop-loss and position sizing
- Maximum 3 trades per day
- 2.5:1 minimum risk-reward ratio

### Telegram Interface
Commands include: `/start`, `/help`, `/status`, `/performance`, `/signals`, `/trades`, `/settings`
- Automatic daily reports at 8:00 UTC
- Weekly reports on Sundays at 10:00 UTC
- Interactive trade confirmation system

### Data Flow
1. Market data collected from multiple sources with failover
2. Strategy manager analyzes data using weighted indicators
3. Signals generated when confluence threshold met
4. Telegram bot sends formatted signals with interactive buttons
5. Performance tracking and reporting runs continuously
6. Adaptive learning adjusts strategies based on performance

## Development Notes

### Async Architecture
The entire system is built on asyncio with proper async/await patterns. Components run concurrently and communicate via shared objects passed during initialization.

### Database Design
Uses SQLAlchemy with async support and PostgreSQL. Models include signal tracking, trade execution records, user interactions, and performance metrics.

### Error Handling
Comprehensive error logging with structured logging system. Each component has proper exception handling with graceful degradation.

### Testing Strategy
The codebase includes pytest configuration with async support, coverage reporting, and specific test structure for trading components.

### Deployment Platform
Designed for Render platform with health check endpoints, proper environment variable handling, and automatic database initialization.
