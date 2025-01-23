import requests
import json
from datetime import datetime

class DeepSeekClient:
    def __init__(self):
        self.url = "https://api.hyperbolic.xyz/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtYW5saWtlbWFpbmdpQGdtYWlsLmNvbSIsImlhdCI6MTczNTMxNDIwMX0.dy4jANPuzStUYy46hyD5HUVm0mHBZ0aidd7B55wvpIw"
        }
        
    def analyze_market_sentiment(self, price_data, technical_signals):
        """
        Analyze market sentiment using DeepSeek AI
        
        Args:
            price_data (dict): Recent price and volume data
            technical_signals (dict): Technical analysis signals
            
        Returns:
            dict: AI analysis results
        """
        # Prepare market context
        market_context = self._prepare_market_context(price_data, technical_signals)
        
        # Create prompt for the AI
        prompt = self._create_analysis_prompt(market_context)
        
        try:
            response = self._query_deepseek(prompt)
            return self._parse_ai_response(response)
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            return None
            
    def predict_price_movement(self, historical_data, timeframe='1h'):
        """
        Get AI prediction for price movement
        
        Args:
            historical_data (dict): Historical price and volume data
            timeframe (str): Timeframe for prediction
            
        Returns:
            dict: Prediction results
        """
        prompt = self._create_prediction_prompt(historical_data, timeframe)
        
        try:
            response = self._query_deepseek(prompt)
            return self._parse_ai_response(response)
        except Exception as e:
            print(f"Error in price prediction: {e}")
            return None
            
    def _prepare_market_context(self, price_data, technical_signals):
        """Prepare market context for AI analysis"""
        return {
            "current_price": price_data.get("close", 0),
            "24h_change": price_data.get("price_change_percent", 0),
            "volume": price_data.get("volume", 0),
            "technical_signals": {
                "trend": "bullish" if technical_signals.get("uptrend", False) else "bearish",
                "rsi": technical_signals.get("rsi", 50),
                "macd_crossover": technical_signals.get("macd_crossover", False),
                "volume_analysis": "high" if technical_signals.get("high_volume", False) else "normal"
            }
        }
        
    def _create_analysis_prompt(self, market_context):
        """Create prompt for market analysis"""
        return f"""Analyze the current market conditions for SUI/USDT:

Current Price: ${market_context['current_price']}
24h Change: {market_context['24h_change']}%
Volume: {market_context['volume']}

Technical Indicators:
- Trend: {market_context['technical_signals']['trend']}
- RSI: {market_context['technical_signals']['rsi']}
- MACD Crossover: {'Yes' if market_context['technical_signals']['macd_crossover'] else 'No'}
- Volume: {market_context['technical_signals']['volume_analysis']}

Please provide:
1. Market sentiment analysis
2. Key support and resistance levels
3. Short-term price prediction
4. Risk assessment
5. Recommended trading strategy"""
        
    def _create_prediction_prompt(self, historical_data, timeframe):
        """Create prompt for price prediction"""
        return f"""Based on the historical data for SUI/USDT:

Timeframe: {timeframe}
Last Traded Price: ${historical_data.get('last_price', 0)}
24h High: ${historical_data.get('high', 0)}
24h Low: ${historical_data.get('low', 0)}
24h Volume: {historical_data.get('volume', 0)}

Please predict:
1. Price direction for next {timeframe}
2. Potential price targets
3. Key levels to watch
4. Risk factors
5. Confidence level in prediction"""
        
    def _query_deepseek(self, prompt):
        """Send query to DeepSeek API"""
        data = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": "deepseek-ai/DeepSeek-V3",
            "max_tokens": 512,
            "temperature": 0.1,
            "top_p": 0.9
        }
        
        response = requests.post(self.url, headers=self.headers, json=data)
        return response.json()
        
    def _parse_ai_response(self, response):
        """Parse and structure AI response"""
        try:
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # Extract key insights from the AI response
            insights = {
                'timestamp': datetime.now().isoformat(),
                'raw_analysis': content,
                'sentiment': self._extract_sentiment(content),
                'confidence_score': self._extract_confidence(content),
                'key_levels': self._extract_key_levels(content),
                'recommendations': self._extract_recommendations(content)
            }
            
            return insights
            
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return None
            
    def _extract_sentiment(self, content):
        """Extract sentiment from AI response"""
        content = content.lower()
        
        # Simple sentiment analysis
        bullish_keywords = ['bullish', 'upward', 'growth', 'increase', 'higher']
        bearish_keywords = ['bearish', 'downward', 'decline', 'decrease', 'lower']
        
        bullish_count = sum(1 for word in bullish_keywords if word in content)
        bearish_count = sum(1 for word in bearish_keywords if word in content)
        
        if bullish_count > bearish_count:
            return 'bullish'
        elif bearish_count > bullish_count:
            return 'bearish'
        return 'neutral'
        
    def _extract_confidence(self, content):
        """Extract confidence score from AI response"""
        # Simple confidence scoring based on language used
        high_confidence = ['confident', 'strong', 'clear', 'definitely']
        medium_confidence = ['likely', 'probable', 'possible']
        low_confidence = ['uncertain', 'unclear', 'might', 'maybe']
        
        content = content.lower()
        
        high_count = sum(1 for word in high_confidence if word in content)
        medium_count = sum(1 for word in medium_confidence if word in content)
        low_count = sum(1 for word in low_confidence if word in content)
        
        total = high_count + medium_count + low_count
        if total == 0:
            return 0.5
            
        return (high_count * 1.0 + medium_count * 0.6 + low_count * 0.2) / total
        
    def _extract_key_levels(self, content):
        """Extract key price levels from AI response"""
        import re
        
        # Look for price levels in the content
        price_pattern = r'\$(\d+\.?\d*)'
        levels = re.findall(price_pattern, content)
        
        if levels:
            return [float(level) for level in levels]
        return []
        
    def _extract_recommendations(self, content):
        """Extract trading recommendations from AI response"""
        recommendations = []
        
        # Look for common recommendation patterns
        if 'buy' in content.lower() or 'long' in content.lower():
            recommendations.append('consider_long')
        if 'sell' in content.lower() or 'short' in content.lower():
            recommendations.append('consider_short')
        if 'wait' in content.lower() or 'hold' in content.lower():
            recommendations.append('wait_for_confirmation')
            
        return recommendations

if __name__ == "__main__":
    # Test the DeepSeek client
    client = DeepSeekClient()
    
    # Sample data for testing
    price_data = {
        "close": 1.23,
        "price_change_percent": 5.67,
        "volume": 1000000
    }
    
    technical_signals = {
        "uptrend": True,
        "rsi": 65,
        "macd_crossover": True,
        "high_volume": True
    }
    
    # Test market sentiment analysis
    sentiment = client.analyze_market_sentiment(price_data, technical_signals)
    if sentiment:
        print("\nMarket Sentiment Analysis:")
        print(json.dumps(sentiment, indent=2))