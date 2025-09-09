#!/bin/bash

# Telegram Trading Bot Deployment Script for Render

set -e

echo "🚀 Starting deployment process..."

# Check if required environment variables are set
required_vars=("TELEGRAM_BOT_TOKEN" "DATABASE_URL" "ALPHA_VANTAGE_API_KEY")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: $var environment variable is not set"
        exit 1
    fi
done

echo "✅ Environment variables verified"

# Install dependencies
echo "📦 Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

# Run database migrations
echo "🗄️  Running database setup..."
python -c "
import sys
sys.path.append('src')
from database import init_database
init_database()
print('Database initialized successfully')
"

# Verify bot configuration
echo "🤖 Verifying bot configuration..."
python -c "
import sys
sys.path.append('src')
from telegram_handler import verify_bot_token
if verify_bot_token():
    print('✅ Bot token verified')
else:
    print('❌ Bot token verification failed')
    sys.exit(1)
"

# Start the application
echo "🎯 Starting Telegram Trading Bot..."
python bot.py
