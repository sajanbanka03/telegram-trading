# Local Setup Script for Telegram Trading Bot
# Run this script to set up your local development environment

Write-Host "🤖 Setting up Telegram Trading Bot locally..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.11+ first." -ForegroundColor Red
    exit 1
}

# Check if pip is available
try {
    pip --version | Out-Null
    Write-Host "✅ pip is available" -ForegroundColor Green
} catch {
    Write-Host "❌ pip not found. Please ensure pip is installed." -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Create .env file from template
if (!(Test-Path ".env")) {
    if (Test-Path ".env.template") {
        Copy-Item ".env.template" ".env"
        Write-Host "✅ Created .env file from template" -ForegroundColor Green
        Write-Host "⚠️  Please edit .env file with your actual API keys" -ForegroundColor Yellow
    } else {
        Write-Host "❌ .env.template not found" -ForegroundColor Red
    }
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

# Create necessary directories
$directories = @("logs", "data")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir
        Write-Host "✅ Created $dir directory" -ForegroundColor Green
    } else {
        Write-Host "✅ $dir directory already exists" -ForegroundColor Green
    }
}

Write-Host "" 
Write-Host "🎯 Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit the .env file with your API keys" -ForegroundColor White
Write-Host "2. Set up a PostgreSQL database (local or cloud)" -ForegroundColor White
Write-Host "3. Run: python bot.py" -ForegroundColor White
Write-Host ""
Write-Host "🔑 Required API keys to add to .env:" -ForegroundColor Cyan
Write-Host "- TELEGRAM_BOT_TOKEN (from @BotFather)" -ForegroundColor White
Write-Host "- TELEGRAM_CHAT_ID (your chat ID)" -ForegroundColor White
Write-Host "- DATABASE_URL (PostgreSQL connection string)" -ForegroundColor White
Write-Host "- ALPHA_VANTAGE_API_KEY (from alphavantage.co)" -ForegroundColor White
Write-Host "- BYBIT_API_KEY (optional, for crypto data)" -ForegroundColor White
Write-Host "- BYBIT_SECRET_KEY (optional, for crypto data)" -ForegroundColor White
