import unittest

from trading_system import decide_trade


class DecisionEngineTests(unittest.TestCase):
    def test_returns_buy_for_clear_trending_setup(self) -> None:
        payload = {
            "asset": "ABC",
            "market_data": {
                "open": 102,
                "high": 103.5,
                "low": 101.8,
                "close": 103,
                "volume": 1500000,
                "average_volume": 1000000,
                "volatility": 1.6,
            },
            "technical_signals": {
                "rsi": 60,
                "ema_trend": "bullish",
                "macd": "bullish",
                "support": 101.0,
                "resistance": 109.0,
            },
            "market_context": {
                "index_trend": "bullish",
                "sector_strength": "strong",
                "liquidity": "high",
            },
            "sentiment": {"news_sentiment": "positive"},
            "user_profile": {
                "capital": 100000,
                "risk_per_trade_pct": 1,
                "risk_level": "medium",
            },
        }

        result = decide_trade(payload)

        self.assertEqual(result["action"], "BUY")
        self.assertIn("confidence", result)
        self.assertIn("position_size", result)

    def test_rejects_conflicting_setup(self) -> None:
        payload = {
            "asset": "ABC",
            "market_data": {
                "open": 100,
                "high": 106,
                "low": 97,
                "close": 99,
                "volume": 600000,
                "average_volume": 1000000,
                "volatility": 4.1,
            },
            "technical_signals": {
                "rsi": 50,
                "ema_trend": "bullish",
                "macd": "bearish",
                "support": 96,
                "resistance": 102,
            },
            "market_context": {
                "index_trend": "neutral",
                "sector_strength": "neutral",
                "liquidity": "medium",
            },
            "sentiment": {"news_sentiment": "neutral"},
            "user_profile": {
                "capital": 100000,
                "risk_per_trade_pct": 1,
                "risk_level": "low",
            },
        }

        result = decide_trade(payload)

        self.assertEqual(result["action"], "NO TRADE")

    def test_rejects_poor_reward_to_risk(self) -> None:
        payload = {
            "asset": "ABC",
            "market_data": {
                "open": 100,
                "high": 102,
                "low": 99,
                "close": 101,
                "volume": 1600000,
                "average_volume": 1000000,
                "volatility": 1.2,
            },
            "technical_signals": {
                "rsi": 58,
                "ema_trend": "bullish",
                "macd": "bullish",
                "support": 99.5,
                "resistance": 103,
            },
            "market_context": {
                "index_trend": "bullish",
                "sector_strength": "strong",
                "liquidity": "high",
            },
            "sentiment": {"news_sentiment": "positive"},
            "user_profile": {
                "capital": 100000,
                "risk_per_trade_pct": 1,
                "risk_level": "medium",
            },
        }

        result = decide_trade(payload)

        self.assertEqual(result["action"], "NO TRADE")


if __name__ == "__main__":
    unittest.main()
