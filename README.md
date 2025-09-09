# Telegram Trading Bot 🤖

A sophisticated trading bot that provides forex and cryptocurrency signals via Telegram, featuring adaptive machine learning strategies and comprehensive performance tracking.

## 🎯 Key Features

- **Multi-Asset Support**: Major forex pairs, Gold (XAUUSD), and cryptocurrencies
- **Target Performance**: 50-80 pips daily profit with 1-3 high-quality signals
- **Adaptive Learning**: Self-adjusting strategies based on performance feedback
- **Confluence Analysis**: Multiple technical indicators with weighted scoring
- **Risk Management**: Built-in stop-loss and position sizing
- **Performance Tracking**: Daily and weekly P&L reports
- **Trade Confirmation**: Interactive Telegram interface for trade tracking
- **Secondary Signals**: Backup signals after 4 hours if primary not taken
- **Strategy Adaptation**: Auto-switching after 3 consecutive days without signals

## 📊 Supported Markets

### Forex (Major Pairs)
- EUR/USD, GBP/USD, USD/JPY
- USD/CHF, AUD/USD, USD/CAD, NZD/USD

### Commodities
- Gold (XAU/USD)

### Cryptocurrencies
- BTC/USDT, ETH/USDT, ADA/USDT, DOT/USDT

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL database
- Telegram Bot Token
- API keys for market data sources

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd telegram-trading-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   ```bash
   cp .env.template .env
   # Edit .env with your API keys and configuration
   ```

4. **Run the bot**
   ```bash
   python bot.py
   ```

## 🌐 Render Platform Deployment

### One-Click Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Manual Deployment Steps

1. **Create Render Account**
   - Sign up at [render.com](https://render.com)
   - Connect your GitHub account

2. **Create PostgreSQL Database**
   - Go to Render Dashboard
   - Click "New" → "PostgreSQL"
   - Choose a plan (free tier available)
   - Note the database connection details

3. **Create Web Service**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Configure the service:
     - **Name**: `telegram-trading-bot`
     - **Environment**: `Python`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python bot.py`
     - **Python Version**: `3.11.0`

4. **Set Environment Variables**
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   DATABASE_URL=your_postgresql_url_here
   ALPHA_VANTAGE_API_KEY=your_api_key_here
   BYBIT_API_KEY=your_bybit_api_key
   BYBIT_SECRET_KEY=your_bybit_secret_key
   ENVIRONMENT=production
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Monitor logs for successful startup

## 🔑 API Keys Setup

### 1. Telegram Bot Token

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Use `/newbot` command
3. Follow prompts to create your bot
4. Save the token provided

### 2. Get Your Chat ID

1. Message your bot first
2. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Look for `"chat":{"id":` in the response
4. Use this number as your `TELEGRAM_CHAT_ID`

### 3. Alpha Vantage API Key (Primary Data Source)

1. Visit [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Get free API key (500 requests/day)
3. For production, consider premium plan

### 4. Bybit API Keys (Crypto Data)

1. Create Bybit account
2. Go to Account → API Management (https://www.bybit.com/app/user/api-management)
3. Create new API key
4. Enable "Reading" permission only (for safety)
5. Whitelist your server IP if possible

### 5. OANDA API Keys (Optional - Forex Data)

1. Create OANDA practice account
2. Generate API token in account settings
3. Note your account ID

## ⚙️ Configuration

### Main Configuration (`config/config.yaml`)

Key settings you can modify:

```yaml
trading:
  target_pips:
    min: 50
    max: 80
  
  risk_management:
    max_risk_per_trade: 2.0  # % of account
    max_daily_trades: 3
    stop_loss_pips: 30

strategy:
  adaptation:
    no_signal_threshold_days: 3
    min_win_rate: 60

telegram:
  signal_send_times: ["09:00", "13:00", "17:00"]
  daily_report_time: "08:00"
```

### Environment Variables

Required variables for production:

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | ✅ |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID | ✅ |
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `ALPHA_VANTAGE_API_KEY` | Primary market data source | ✅ |
| `BYBIT_API_KEY` | Crypto market data | ❌ |
| `BYBIT_SECRET_KEY` | Crypto market data | ❌ |
| `OANDA_API_KEY` | Forex market data | ❌ |
| `OANDA_ACCOUNT_ID` | OANDA account ID | ❌ |

## 🤖 Bot Commands

### Basic Commands

- `/start` - Welcome message and bot introduction
- `/help` - List all available commands
- `/status` - Current bot status and health
- `/performance` - Performance metrics and statistics

### Trading Commands

- `/signals` - View recent trading signals
- `/trades` - View trade history and outcomes
- `/settings` - Configure bot settings

### Reports

- **Daily Reports**: Sent automatically at 8:00 UTC
- **Weekly Reports**: Sent every Sunday at 10:00 UTC

## 📈 Strategy Overview

### Multi-Confluence Analysis

The bot uses multiple technical indicators with weighted scoring:

1. **RSI (15% weight)**: Overbought/oversold conditions
2. **MACD (20% weight)**: Momentum and trend direction  
3. **Bollinger Bands (15% weight)**: Volatility and mean reversion
4. **Support/Resistance (25% weight)**: Key price levels
5. **Fibonacci Retracements (15% weight)**: Retracement levels
6. **Volume Analysis (10% weight)**: Volume confirmation

### Adaptive Learning

- **Performance Monitoring**: Continuous tracking of strategy effectiveness
- **Auto-Adaptation**: Switches strategies after 3 days without signals
- **Backtesting**: Evaluates strategy performance before switching
- **Stop-Loss Learning**: Adjusts parameters based on SL hits

### Signal Quality

- **Minimum Confluence**: 70% score required for signals
- **Risk-Reward Ratio**: Minimum 2.5:1 target
- **Position Sizing**: 2% maximum risk per trade

## 📊 Performance Tracking

### Key Metrics

- **Daily P&L**: Pips gained/lost per day
- **Win Rate**: Percentage of winning trades
- **Risk-Reward Ratio**: Average profit vs loss ratio
- **Strategy Performance**: Individual strategy statistics
- **Confluence Accuracy**: Signal quality tracking

### Reporting Features

- **Real-time Updates**: Live P&L tracking
- **Historical Analysis**: Performance trends over time
- **Strategy Comparison**: Compare different strategies
- **Trade Journal**: Detailed trade log with entry/exit reasons

## 🔧 Development

### Project Structure

```
telegram-trading-bot/
├── bot.py                 # Main entry point
├── src/                   # Source code
│   ├── telegram_handler.py   # Telegram bot interface
│   ├── strategy.py           # Trading strategies
│   ├── data_handler.py       # Market data collection
│   ├── database.py           # Database models
│   ├── reporting.py          # Performance reports
│   └── logger.py            # Logging system
├── config/                # Configuration files
├── deployment/            # Deployment scripts
├── logs/                  # Log files
├── data/                  # Market data cache
├── tests/                 # Unit tests
└── docs/                  # Documentation
```

### Adding New Features

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Implement changes** with proper tests
4. **Submit pull request** with detailed description

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_strategy.py
```

## 🐛 Troubleshooting

### Common Issues

**Bot not starting:**
- Check environment variables are set correctly
- Verify database connection
- Confirm Telegram bot token is valid

**No signals generated:**
- Check market data connections
- Verify API key limits haven't been exceeded
- Review confluence threshold settings

**Database errors:**
- Ensure PostgreSQL is running
- Check DATABASE_URL format
- Verify database permissions

**Telegram not responding:**
- Confirm bot token is correct
- Check chat ID is accurate
- Verify bot has been started with /start command

### Logs

Check application logs for detailed error information:

```bash
# Main application log
tail -f logs/bot.log

# Trading-specific log
tail -f logs/trades.log

# Error log
tail -f logs/errors.log
```

### Health Check

The bot includes health check endpoints for monitoring:

- **Health Check**: `https://your-app.render.com/health`
- **Status**: `https://your-app.render.com/`

## 📞 Support

### Documentation

- **Configuration Guide**: See `config/config.yaml` comments
- **API Documentation**: Check individual module docstrings
- **Database Schema**: See `src/database.py` models

### Getting Help

1. **Check logs** for error messages
2. **Review configuration** settings
3. **Test API connections** individually
4. **Verify environment variables**

### Contributing

We welcome contributions! Please:

1. **Fork the repository**
2. **Create feature branch**
3. **Add tests** for new functionality
4. **Update documentation**
5. **Submit pull request**

## ⚖️ Disclaimer

**Important**: This trading bot is for educational and informational purposes only. Trading forex and cryptocurrencies involves substantial risk of loss and may not be suitable for all investors. Past performance does not guarantee future results. Always conduct your own research and consider your risk tolerance before trading.

**Risk Warning**:
- Never invest more than you can afford to lose
- Trading signals are not guaranteed to be profitable
- Market conditions can change rapidly
- Always use proper risk management

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Technical Analysis Libraries**: TA-Lib, pandas-ta
- **Telegram Bot Framework**: python-telegram-bot
- **Market Data Providers**: Alpha Vantage, Bybit, OANDA
- **Deployment Platform**: Render
- **Database**: PostgreSQL

---

**Made with ❤️ for traders who want consistent, high-quality signals**

Happy Trading! 🚀📈
