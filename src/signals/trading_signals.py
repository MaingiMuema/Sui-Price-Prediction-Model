from datetime import datetime
import pandas as pd
import numpy as np
from ..data.binance_client import BinanceClient
from ..analysis.technical_indicators import TechnicalAnalysis
from ..ai.deepseek_client import DeepSeekClient

class SignalGenerator:
    def __init__(self, timeframe='1h'):
        self.binance_client = BinanceClient()
        self.deepseek_client = DeepSeekClient()
        self.timeframe = timeframe
        self.risk_reward_ratio = 2.0
        self.min_confidence_threshold = 0.7
        
    def generate_trading_signal(self, lookback_days=30):
        """
        Generate trading signal combining technical and AI analysis
        
        Returns:
            dict: Trading signal with entry/exit points
        """
        try:
            # Get historical data
            df = self.binance_client.get_historical_klines(
                interval=self.timeframe,
                lookback_days=lookback_days
            )
            
            if df is None:
                raise Exception("Failed to fetch historical data")
                
            # Get current market data
            current_price = self.binance_client.get_current_price()
            market_stats = self.binance_client.get_24h_stats()
            
            if current_price is None or market_stats is None:
                raise Exception("Failed to fetch current market data")
                
            # Perform technical analysis
            ta = TechnicalAnalysis(df)
            ta.add_all_indicators()
            technical_signals = ta.generate_signals()
            
            # Get latest signals
            latest_signals = technical_signals.iloc[-1].to_dict()
            
            # Prepare data for AI analysis
            price_data = {
                "close": current_price,
                "price_change_percent": market_stats['price_change_percent'],
                "volume": market_stats['volume']
            }
            
            # Get AI analysis
            ai_analysis = self.deepseek_client.analyze_market_sentiment(
                price_data,
                latest_signals
            )
            
            if ai_analysis is None:
                raise Exception("Failed to get AI analysis")
                
            # Generate final signal
            signal = self._generate_final_signal(
                current_price,
                latest_signals,
                ai_analysis,
                ta
            )
            
            return signal
            
        except Exception as e:
            print(f"Error generating trading signal: {e}")
            return None
            
    def _generate_final_signal(self, current_price, technical_signals, ai_analysis, ta):
        """
        Combine technical and AI analysis to generate final trading signal
        """
        # Initialize signal confidence scores
        bull_score = 0
        bear_score = 0
        
        # Technical Analysis Scoring (50% weight)
        if technical_signals.get('uptrend', False):
            bull_score += 0.25
        if technical_signals.get('downtrend', False):
            bear_score += 0.25
            
        if technical_signals.get('golden_cross', False):
            bull_score += 0.15
        if technical_signals.get('death_cross', False):
            bear_score += 0.15
            
        if technical_signals.get('rsi_oversold', False):
            bull_score += 0.1
        if technical_signals.get('rsi_overbought', False):
            bear_score += 0.1
            
        # AI Analysis Scoring (50% weight)
        ai_confidence = ai_analysis.get('confidence_score', 0.5)
        if ai_analysis.get('sentiment') == 'bullish':
            bull_score += 0.5 * ai_confidence
        elif ai_analysis.get('sentiment') == 'bearish':
            bear_score += 0.5 * ai_confidence
            
        # Determine signal type
        signal_type = None
        if bull_score > bear_score and bull_score > self.min_confidence_threshold:
            signal_type = 'buy'
        elif bear_score > bull_score and bear_score > self.min_confidence_threshold:
            signal_type = 'sell'
            
        if signal_type is None:
            return {
                'timestamp': datetime.now().isoformat(),
                'signal': 'neutral',
                'message': 'No clear trading opportunity',
                'confidence': max(bull_score, bear_score)
            }
            
        # Calculate trade targets
        targets = ta.calculate_trade_targets(
            current_price,
            trend='long' if signal_type == 'buy' else 'short',
            risk_reward_ratio=self.risk_reward_ratio
        )
        
        # Get key levels from AI analysis
        key_levels = ai_analysis.get('key_levels', [])
        
        return {
            'timestamp': datetime.now().isoformat(),
            'signal': signal_type,
            'current_price': current_price,
            'confidence': bull_score if signal_type == 'buy' else bear_score,
            'entry': {
                'price': current_price,
                'type': 'market',
                'timing': self._get_entry_timing(technical_signals, ai_analysis)
            },
            'targets': {
                'stop_loss': targets['stop_loss'],
                'take_profit': targets['take_profit']
            },
            'risk_reward_ratio': self.risk_reward_ratio,
            'key_levels': key_levels,
            'technical_factors': {
                'trend': 'bullish' if technical_signals.get('uptrend', False) else 'bearish',
                'rsi_condition': 'oversold' if technical_signals.get('rsi_oversold', False) else 
                                'overbought' if technical_signals.get('rsi_overbought', False) else 'neutral',
                'volume_condition': 'high' if technical_signals.get('high_volume', False) else 'normal'
            },
            'ai_analysis': {
                'sentiment': ai_analysis.get('sentiment'),
                'confidence': ai_analysis.get('confidence_score'),
                'recommendations': ai_analysis.get('recommendations', [])
            }
        }
        
    def _get_entry_timing(self, technical_signals, ai_analysis):
        """Determine optimal entry timing"""
        if technical_signals.get('high_volume', False) and \
           ai_analysis.get('confidence_score', 0) > 0.8:
            return 'immediate'
            
        conditions = []
        if technical_signals.get('rsi_oversold', False):
            conditions.append('wait for RSI recovery')
        if technical_signals.get('rsi_overbought', False):
            conditions.append('wait for RSI pullback')
        if not technical_signals.get('high_volume', False):
            conditions.append('wait for volume confirmation')
            
        return 'delayed: ' + ', '.join(conditions) if conditions else 'immediate'

if __name__ == "__main__":
    # Test the signal generator
    generator = SignalGenerator(timeframe='1h')
    signal = generator.generate_trading_signal(lookback_days=7)
    
    if signal:
        print("\nTrading Signal Generated:")
        print("Signal:", signal['signal'])
        print("Confidence:", f"{signal['confidence']:.2%}")
        print("\nEntry Point:")
        print("Price:", signal['entry']['price'])
        print("Timing:", signal['entry']['timing'])
        print("\nTargets:")
        print("Stop Loss:", signal['targets']['stop_loss'])
        print("Take Profit:", signal['targets']['take_profit'])
        print("\nKey Levels:", signal['key_levels'])