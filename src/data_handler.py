"""
Market Data Handler - Multi-source market data collection
Supports Alpha Vantage (forex), Bybit (crypto), and OANDA (forex)
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from logger import get_trading_logger

try:
    from pybit.unified_trading import HTTP as BybitClient
except ImportError:
    BybitClient = None
    
try:
    from alpha_vantage.timeseries import TimeSeries
except ImportError:
    TimeSeries = None

logger = get_trading_logger()

class MarketDataHandler:
    """Handles market data collection from multiple sources"""
    
    def __init__(self):
        self.running = False
        self.data_sources = {}
        self.crypto_pairs = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT']
        self.forex_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD']
        self.commodities = ['XAUUSD']
        
        self._initialize_clients()
        logger.log_system_event("MarketDataHandler initialized")
    
    def _initialize_clients(self):
        """Initialize API clients for different data sources"""
        try:
            # Initialize Bybit client for crypto data
            bybit_api_key = os.getenv('BYBIT_API_KEY')
            bybit_secret = os.getenv('BYBIT_SECRET_KEY')
            
            if bybit_api_key and bybit_secret and BybitClient:
                self.data_sources['bybit'] = BybitClient(
                    api_key=bybit_api_key,
                    api_secret=bybit_secret,
                    testnet=os.getenv('BYBIT_TESTNET', 'false').lower() == 'true'
                )
                logger.log_system_event("Bybit client initialized successfully")
            else:
                logger.log_system_event("Bybit client not initialized - missing credentials or pybit library")
            
            # Initialize Alpha Vantage for forex/commodities
            alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
            if alpha_vantage_key and TimeSeries:
                self.data_sources['alpha_vantage'] = TimeSeries(
                    key=alpha_vantage_key,
                    output_format='pandas'
                )
                logger.log_system_event("Alpha Vantage client initialized successfully")
            else:
                logger.log_system_event("Alpha Vantage client not initialized - missing credentials or library")
                
        except Exception as e:
            logger.log_error(e, {"context": "data_source_initialization"})
    
    async def get_crypto_data(self, symbol: str, interval: str = '1') -> Optional[Dict[str, Any]]:
        """Get cryptocurrency data from Bybit"""
        if 'bybit' not in self.data_sources:
            logger.log_system_event(f"Bybit client not available for {symbol}")
            return None
            
        try:
            client = self.data_sources['bybit']
            
            # Get kline data from Bybit
            response = client.get_kline(
                category="spot",
                symbol=symbol,
                interval=interval,
                limit=200
            )
            
            if response.get('retCode') == 0:
                klines = response.get('result', {}).get('list', [])
                if klines:
                    logger.log_system_event(f"Retrieved {len(klines)} data points for {symbol}")
                    return {
                        'symbol': symbol,
                        'data': klines,
                        'timestamp': datetime.now(timezone.utc),
                        'source': 'bybit'
                    }
            else:
                logger.log_system_event(f"Bybit API error for {symbol}: {response.get('retMsg')}")
                
        except Exception as e:
            logger.log_error(e, {"context": f"bybit_data_fetch_{symbol}"})
            
        return None
    
    async def get_forex_data(self, symbol: str, interval: str = '1min') -> Optional[Dict[str, Any]]:
        """Get forex data from Alpha Vantage"""
        if 'alpha_vantage' not in self.data_sources:
            logger.log_system_event(f"Alpha Vantage client not available for {symbol}")
            return None
            
        try:
            client = self.data_sources['alpha_vantage']
            
            # Get intraday data from Alpha Vantage
            data, meta_data = client.get_intraday(
                symbol=symbol,
                interval=interval,
                outputsize='compact'
            )
            
            if not data.empty:
                logger.log_system_event(f"Retrieved {len(data)} data points for {symbol}")
                return {
                    'symbol': symbol,
                    'data': data,
                    'meta_data': meta_data,
                    'timestamp': datetime.now(timezone.utc),
                    'source': 'alpha_vantage'
                }
                
        except Exception as e:
            logger.log_error(e, {"context": f"alpha_vantage_data_fetch_{symbol}"})
            
        return None
    
    async def get_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get market data for any supported symbol from appropriate source"""
        if symbol in self.crypto_pairs:
            return await self.get_crypto_data(symbol)
        elif symbol in self.forex_pairs or symbol in self.commodities:
            return await self.get_forex_data(symbol)
        else:
            logger.log_system_event(f"Unsupported symbol: {symbol}")
            return None
    
    async def start_data_collection(self):
        """Start collecting market data from all configured sources"""
        self.running = True
        logger.log_system_event("Market data collection started")
        
        while self.running:
            try:
                # Collect data for all supported instruments
                all_symbols = self.crypto_pairs + self.forex_pairs + self.commodities
                
                for symbol in all_symbols:
                    if not self.running:
                        break
                        
                    data = await self.get_market_data(symbol)
                    if data:
                        # Here you would typically store the data or pass it to strategy manager
                        logger.log_system_event(f"Collected data for {symbol}")
                    
                    # Small delay between requests to respect rate limits
                    await asyncio.sleep(2)
                
                # Wait before next collection cycle
                await asyncio.sleep(300)  # 5 minutes between cycles
                
            except Exception as e:
                logger.log_error(e, {"context": "data_collection_cycle"})
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def stop(self):
        """Stop data collection"""
        self.running = False
        logger.log_system_event("Market data collection stopped")
