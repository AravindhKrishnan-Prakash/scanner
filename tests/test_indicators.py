import unittest

from trading_system.indicators import adx, ema, macd, rsi
from trading_system.live_models import Candle


class IndicatorTests(unittest.TestCase):
    def test_ema_tracks_latest_value(self) -> None:
        result = ema([10, 11, 12, 13, 14], 3)
        self.assertEqual(len(result), 5)
        self.assertGreater(result[-1], result[0])

    def test_rsi_stays_in_bounds(self) -> None:
        value = rsi([100, 101, 102, 103, 105, 104, 106, 108, 109, 111, 110, 112, 114, 115, 116])
        self.assertGreaterEqual(value, 0)
        self.assertLessEqual(value, 100)

    def test_macd_returns_histogram(self) -> None:
        closes = [100 + index for index in range(40)]
        result = macd(closes)
        self.assertIn("histogram", result)

    def test_adx_calculates_positive_value(self) -> None:
        candles = [
            Candle(f"2026-01-{index + 1:02d}", 100 + index, 102 + index, 99 + index, 101 + index, 1000 + index * 10)
            for index in range(40)
        ]
        value = adx(candles)
        self.assertGreaterEqual(value, 0)


if __name__ == "__main__":
    unittest.main()
