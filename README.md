# Sui Price Prediction Model

A sophisticated trading signal generator for SUI/USDT that combines technical analysis with DeepSeek AI for enhanced decision making.

## Features

- Real-time and historical data from Binance
- Advanced technical analysis indicators
- AI-powered sentiment analysis and pattern recognition
- Dynamic support/resistance level detection
- Smart entry/exit point calculation
- Risk management with stop-loss and take-profit targets
- Configurable timeframes and parameters

## Technical Indicators

- Moving Averages (EMA/SMA)
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Volume Analysis
- Support/Resistance Levels

## AI Features

- Market sentiment analysis
- Pattern recognition
- Price movement prediction
- Risk assessment
- Trading strategy recommendations

## Requirements

- Python 3.8+
- Binance API credentials
- DeepSeek API access

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/Sui-Price-Prediction-Model.git
cd Sui-Price-Prediction-Model
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure your API credentials in `.env`:

```
API_Key=your_binance_api_key
Secret_Key=your_binance_secret_key
```

## Configuration

The bot can be configured through `config/trading_config.json`:

```json
{
  "timeframe": "1h",
  "lookback_days": 30,
  "update_interval": 300,
  "signal_threshold": 0.7,
  "risk_reward_ratio": 2.0,
  "notifications": true
}
```

- `timeframe`: Trading interval (1m, 5m, 15m, 1h, 4h, 1d)
- `lookback_days`: Historical data period for analysis
- `update_interval`: Time between signal updates (seconds)
- `signal_threshold`: Minimum confidence for signal generation
- `risk_reward_ratio`: Take profit to stop loss ratio
- `notifications`: Enable/disable signal notifications

## Usage

Run the trading bot:

```bash
python main.py
```

The bot will:

1. Fetch historical data from Binance
2. Perform technical analysis
3. Get AI insights from DeepSeek
4. Generate trading signals
5. Save signals to the `signals` directory
6. Update at configured intervals

## Trading Signals

Each signal includes:

- Signal type (buy/sell)
- Confidence score
- Entry point and timing
- Stop-loss and take-profit targets
- Technical analysis factors
- AI sentiment analysis
- Key price levels

## Project Structure

```
sui-trading-bot/
├── src/
│   ├── data/
│   │   └── binance_client.py    # Binance API integration
│   ├── analysis/
│   │   └── technical_indicators.py    # Technical analysis
│   ├── ai/
│   │   └── deepseek_client.py    # AI integration
│   └── signals/
│       └── trading_signals.py    # Signal generation
├── config/
│   └── trading_config.json    # Bot configuration
├── signals/    # Generated trading signals
├── requirements.txt
├── .env    # API credentials
└── main.py    # Main application
```

## Disclaimer

This bot is for informational purposes only. Always perform your own analysis and risk assessment before trading. Cryptocurrency trading involves substantial risk of loss and is not suitable for all investors.

## License

MIT License - feel free to use and modify as needed.
