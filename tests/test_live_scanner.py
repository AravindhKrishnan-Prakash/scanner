import unittest

from trading_system.config import RuntimeConfig, ScannerSettings, UserProfile, WatchlistItem
from trading_system.live_scanner import LiveScannerService
from trading_system.sample_provider import SampleMarketProvider


class LiveScannerTests(unittest.TestCase):
    def test_scanner_returns_dashboard_shape(self) -> None:
        config = RuntimeConfig(
            market_index_query="NIFTY 50",
            watchlist=[WatchlistItem(query="RELIANCE"), WatchlistItem(query="TCS")],
            user_profile=UserProfile(capital=100000, risk_per_trade_pct=1, risk_level="low"),
            scanner=ScannerSettings(poll_seconds=30, history_days=90, support_resistance_lookback=20),
        )

        service = LiveScannerService(SampleMarketProvider(), config)
        snapshot = service.run_scan()

        self.assertIn("market", snapshot)
        self.assertIn("watchlist", snapshot)
        self.assertIn("opportunities", snapshot)
        self.assertGreaterEqual(len(snapshot["watchlist"]), 2)


if __name__ == "__main__":
    unittest.main()
