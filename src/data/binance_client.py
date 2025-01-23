from binance.client import Client
from binance.enums import *
from datetime import datetime, timedelta
import pandas as pd
import os
from dotenv import load_dotenv

class BinanceClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('API_Key')
        self.api_secret = os.getenv('Secret_Key')
        self.client = Client(self.api_key, self.api_secret)
        self.symbol = 'SUIUSDT'
        
    def get_historical_klines(self, interval='1h', lookback_days=30):
        """
        Fetch historical klines/candlestick data
        
        Args:
            interval (str): Kline interval (1m, 5m, 15m, 1h, 4h, 1d)
            lookback_days (int): Number of days to look back
            
        Returns:
            pd.DataFrame: DataFrame with OHLCV data
        """
        try:
            # Calculate start time
            start_time = datetime.now() - timedelta(days=lookback_days)
            
            # Get klines
            klines = self.client.get_historical_klines(
                symbol=self.symbol,
                interval=interval,
                start_str=start_time.strftime("%d %b %Y %H:%M:%S"),
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Convert string values to float
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
                
            return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return None
            
    def get_current_price(self):
        """Get current price of SUI/USDT"""
        try:
            ticker = self.client.get_symbol_ticker(symbol=self.symbol)
            return float(ticker['price'])
        except Exception as e:
            print(f"Error fetching current price: {e}")
            return None
            
    def get_recent_trades(self, limit=100):
        """Get recent trades"""
        try:
            trades = self.client.get_recent_trades(symbol=self.symbol, limit=limit)
            return pd.DataFrame(trades)
        except Exception as e:
            print(f"Error fetching recent trades: {e}")
            return None
            
    def get_order_book(self, limit=100):
        """Get current order book"""
        try:
            depth = self.client.get_order_book(symbol=self.symbol, limit=limit)
            return {
                'bids': pd.DataFrame(depth['bids'], columns=['price', 'quantity']),
                'asks': pd.DataFrame(depth['asks'], columns=['price', 'quantity'])
            }
        except Exception as e:
            print(f"Error fetching order book: {e}")
            return None
    
    def get_24h_stats(self):
        """Get 24-hour price statistics"""
        try:
            stats = self.client.get_ticker(symbol=self.symbol)
            return {
                'price_change': float(stats['priceChange']),
                'price_change_percent': float(stats['priceChangePercent']),
                'high': float(stats['highPrice']),
                'low': float(stats['lowPrice']),
                'volume': float(stats['volume']),
                'trades': int(stats['count'])
            }
        except Exception as e:
            print(f"Error fetching 24h stats: {e}")
            return None

if __name__ == "__main__":
    # Test the client
    client = BinanceClient()
    print("Current SUI price:", client.get_current_price())
    df = client.get_historical_klines(interval='1h', lookback_days=7)
    if df is not None:
        print("\nRecent price data:")
        print(df.tail())