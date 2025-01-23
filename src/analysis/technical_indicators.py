import pandas as pd
import numpy as np
from ta import momentum, trend, volume

class TechnicalAnalysis:
    def __init__(self, df):
        """
        Initialize with OHLCV DataFrame
        
        Args:
            df (pd.DataFrame): DataFrame with columns [timestamp, open, high, low, close, volume]
        """
        self.df = df.copy()
        
    def add_all_indicators(self):
        """Add all technical indicators to the DataFrame"""
        self.add_moving_averages()
        self.add_rsi()
        self.add_macd()
        self.add_volume_indicators()
        return self.df
        
    def add_moving_averages(self, short_window=20, long_window=50):
        """Add EMA and SMA indicators"""
        # Short-term EMAs
        self.df['ema_9'] = trend.ema_indicator(self.df['close'], window=9)
        self.df['ema_20'] = trend.ema_indicator(self.df['close'], window=short_window)
        
        # Long-term EMAs
        self.df['ema_50'] = trend.ema_indicator(self.df['close'], window=long_window)
        self.df['ema_200'] = trend.ema_indicator(self.df['close'], window=200)
        
        # SMAs
        self.df['sma_20'] = trend.sma_indicator(self.df['close'], window=short_window)
        self.df['sma_50'] = trend.sma_indicator(self.df['close'], window=long_window)
        
    def add_rsi(self, window=14):
        """Add RSI indicator"""
        self.df['rsi'] = momentum.rsi(self.df['close'], window=window)
        
    def add_macd(self, fast=12, slow=26, signal=9):
        """Add MACD indicators"""
        self.df['macd_line'] = trend.macd(self.df['close'], 
                                         window_fast=fast, 
                                         window_slow=slow)
        self.df['macd_signal'] = trend.macd_signal(self.df['close'], 
                                                  window_fast=fast, 
                                                  window_slow=slow, 
                                                  window_sign=signal)
        self.df['macd_hist'] = trend.macd_diff(self.df['close'], 
                                              window_fast=fast, 
                                              window_slow=slow, 
                                              window_sign=signal)
        
    def add_volume_indicators(self):
        """Add volume-based indicators"""
        self.df['volume_sma'] = volume.volume_sma_indicator(self.df['close'], 
                                                          self.df['volume'])
        self.df['force_index'] = volume.force_index(self.df['close'], 
                                                   self.df['volume'])
        
    def find_support_resistance(self, window=20, num_points=5):
        """
        Find potential support and resistance levels
        
        Args:
            window (int): Rolling window size
            num_points (int): Number of S/R points to identify
            
        Returns:
            tuple: (support_levels, resistance_levels)
        """
        df = self.df.copy()
        
        # Find local minimums and maximums
        df['min'] = df['low'].rolling(window=window, center=True).min()
        df['max'] = df['high'].rolling(window=window, center=True).max()
        
        # Get unique levels sorted by frequency
        support_levels = df[df['low'] == df['min']]['low'].value_counts()
        resistance_levels = df[df['high'] == df['max']]['high'].value_counts()
        
        return (
            support_levels.head(num_points).index.tolist(),
            resistance_levels.head(num_points).index.tolist()
        )
        
    def generate_signals(self):
        """
        Generate trading signals based on technical indicators
        
        Returns:
            pd.DataFrame: DataFrame with signals
        """
        signals = pd.DataFrame(index=self.df.index)
        signals['timestamp'] = self.df['timestamp']
        
        # RSI signals
        signals['rsi_oversold'] = self.df['rsi'] < 30
        signals['rsi_overbought'] = self.df['rsi'] > 70
        
        # MACD signals
        signals['macd_crossover'] = (self.df['macd_hist'] > 0) & (self.df['macd_hist'].shift(1) < 0)
        signals['macd_crossunder'] = (self.df['macd_hist'] < 0) & (self.df['macd_hist'].shift(1) > 0)
        
        # Moving average signals
        signals['golden_cross'] = (self.df['ema_20'] > self.df['ema_50']) & (self.df['ema_20'].shift(1) <= self.df['ema_50'].shift(1))
        signals['death_cross'] = (self.df['ema_20'] < self.df['ema_50']) & (self.df['ema_20'].shift(1) >= self.df['ema_50'].shift(1))
        
        # Volume signals
        signals['high_volume'] = self.df['volume'] > self.df['volume_sma'] * 1.5
        
        # Trend strength
        signals['uptrend'] = (
            (self.df['ema_20'] > self.df['ema_50']) & 
            (self.df['ema_50'] > self.df['ema_200']) &
            (self.df['close'] > self.df['ema_20'])
        )
        
        signals['downtrend'] = (
            (self.df['ema_20'] < self.df['ema_50']) & 
            (self.df['ema_50'] < self.df['ema_200']) &
            (self.df['close'] < self.df['ema_20'])
        )
        
        return signals
        
    def calculate_trade_targets(self, current_price, trend='long', risk_reward_ratio=2):
        """
        Calculate stop loss and take profit levels
        
        Args:
            current_price (float): Current asset price
            trend (str): 'long' or 'short'
            risk_reward_ratio (float): Ratio of reward to risk
            
        Returns:
            dict: Dictionary with stop loss and take profit levels
        """
        # Get ATR for volatility-based stops
        atr = self.df['high'].rolling(14).max() - self.df['low'].rolling(14).min()
        current_atr = atr.iloc[-1] / self.df['close'].iloc[-1]  # As percentage of price
        
        # Default stop distances based on ATR
        stop_distance = current_price * current_atr * 1.5
        
        if trend == 'long':
            stop_loss = current_price - stop_distance
            take_profit = current_price + (stop_distance * risk_reward_ratio)
        else:  # short
            stop_loss = current_price + stop_distance
            take_profit = current_price - (stop_distance * risk_reward_ratio)
            
        return {
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk_distance': abs(current_price - stop_loss),
            'reward_distance': abs(take_profit - current_price)
        }

if __name__ == "__main__":
    # Test with sample data
    from binance_client import BinanceClient
    
    client = BinanceClient()
    df = client.get_historical_klines(interval='1h', lookback_days=30)
    
    if df is not None:
        ta = TechnicalAnalysis(df)
        ta.add_all_indicators()
        signals = ta.generate_signals()
        
        print("\nRecent signals:")
        print(signals.tail())
        
        current_price = df['close'].iloc[-1]
        targets = ta.calculate_trade_targets(current_price, trend='long')
        print("\nTrade targets for current price:", current_price)
        print(targets)