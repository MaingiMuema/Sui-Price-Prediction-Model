import os
import json
from datetime import datetime
import time
from src.signals.trading_signals import SignalGenerator
from dotenv import load_dotenv

class TradingBot:
    def __init__(self):
        load_dotenv()
        self.config = self._load_config()
        self.signal_generator = SignalGenerator(
            timeframe=self.config['timeframe']
        )
        
    def _load_config(self):
        """Load trading configuration"""
        default_config = {
            'timeframe': '1h',
            'lookback_days': 30,
            'update_interval': 300,  # 5 minutes
            'signal_threshold': 0.7,
            'risk_reward_ratio': 2.0,
            'notifications': True
        }
        
        config_path = 'config/trading_config.json'
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return {**default_config, **json.load(f)}
        except Exception as e:
            print(f"Error loading config: {e}")
            
        return default_config
        
    def _save_signal(self, signal):
        """Save trading signal to file"""
        if signal:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'signals/signal_{timestamp}.json'
            
            os.makedirs('signals', exist_ok=True)
            
            try:
                with open(filename, 'w') as f:
                    json.dump(signal, f, indent=2)
                print(f"Signal saved to {filename}")
            except Exception as e:
                print(f"Error saving signal: {e}")
                
    def _print_signal(self, signal):
        """Print trading signal in a formatted way"""
        if not signal:
            print("\n⚠️  No trading signal generated")
            return
            
        print("\n" + "="*50)
        print(f"🔔 Trading Signal Generated at {signal['timestamp']}")
        print("="*50)
        
        # Signal type and confidence
        signal_emoji = "🟢" if signal['signal'] == 'buy' else "🔴" if signal['signal'] == 'sell' else "⚪"
        print(f"\n{signal_emoji} Signal: {signal['signal'].upper()}")
        print(f"📊 Confidence: {signal['confidence']:.2%}")
        
        # Entry details
        print("\n📍 Entry Point:")
        print(f"  Price: ${signal['entry']['price']:.4f}")
        print(f"  Timing: {signal['entry']['timing']}")
        
        # Targets
        print("\n🎯 Targets:")
        print(f"  Stop Loss: ${signal['targets']['stop_loss']:.4f}")
        print(f"  Take Profit: ${signal['targets']['take_profit']:.4f}")
        print(f"  Risk/Reward Ratio: {signal['risk_reward_ratio']:.1f}")
        
        # Technical Analysis
        print("\n📈 Technical Factors:")
        print(f"  Trend: {signal['technical_factors']['trend']}")
        print(f"  RSI Condition: {signal['technical_factors']['rsi_condition']}")
        print(f"  Volume: {signal['technical_factors']['volume_condition']}")
        
        # AI Analysis
        print("\n🤖 AI Analysis:")
        print(f"  Sentiment: {signal['ai_analysis']['sentiment']}")
        print(f"  Confidence: {signal['ai_analysis']['confidence']:.2%}")
        if signal['ai_analysis']['recommendations']:
            print("  Recommendations:", ", ".join(signal['ai_analysis']['recommendations']))
            
        # Key Levels
        if signal['key_levels']:
            print("\n📊 Key Price Levels:")
            print("  " + ", ".join([f"${level:.4f}" for level in signal['key_levels']]))
            
        print("\n" + "="*50)
        
    def run(self):
        """Run the trading bot"""
        print(f"\n🤖 Starting Sui Trading Signal Bot")
        print(f"⚙️  Timeframe: {self.config['timeframe']}")
        print(f"⏰ Update Interval: {self.config['update_interval']} seconds")
        
        while True:
            try:
                print("\n📊 Generating trading signal...")
                signal = self.signal_generator.generate_trading_signal(
                    lookback_days=self.config['lookback_days']
                )
                
                self._print_signal(signal)
                self._save_signal(signal)
                
                # Wait for next update
                print(f"\n⏳ Waiting {self.config['update_interval']} seconds for next update...")
                time.sleep(self.config['update_interval'])
                
            except KeyboardInterrupt:
                print("\n\n🛑 Bot stopped by user")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("Retrying in 60 seconds...")
                time.sleep(60)

def setup_config():
    """Set up initial configuration"""
    config = {
        'timeframe': '1h',
        'lookback_days': 30,
        'update_interval': 300,
        'signal_threshold': 0.7,
        'risk_reward_ratio': 2.0,
        'notifications': True
    }
    
    os.makedirs('config', exist_ok=True)
    
    with open('config/trading_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    print("Configuration file created at config/trading_config.json")

if __name__ == "__main__":
    # Create config if it doesn't exist
    if not os.path.exists('config/trading_config.json'):
        setup_config()
        
    # Create signals directory if it doesn't exist
    os.makedirs('signals', exist_ok=True)
    
    # Run the bot
    bot = TradingBot()
    bot.run()