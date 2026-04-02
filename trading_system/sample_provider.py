from __future__ import annotations

import math
from datetime import datetime, timedelta
from random import Random
from typing import Dict, List

from .live_models import Candle, QuoteSnapshot, ResolvedInstrument


class SampleMarketProvider:
    name = "sample"

    def __init__(self) -> None:
        self._seed = 7
        self._resolved: Dict[str, ResolvedInstrument] = {}

    def resolve_query(self, query: str, prefer_equity: bool = True) -> ResolvedInstrument:
        normalized = query.strip().upper()
        if normalized in self._resolved:
            return self._resolved[normalized]

        symbol = normalized.replace(" ", "")
        instrument = ResolvedInstrument(query=query, symbol=symbol, instrument_key=f"SAMPLE|{symbol}", name=query.title())
        self._resolved[normalized] = instrument
        return instrument

    def get_bulk_quotes(self, instrument_keys: List[str], interval: str = "1d") -> Dict[str, QuoteSnapshot]:
        quotes: Dict[str, QuoteSnapshot] = {}
        now = datetime.utcnow().isoformat()

        for instrument_key in instrument_keys:
            candles = self.get_historical_daily_candles(instrument_key, "2025-01-01", "2026-12-31")
            last = candles[-1]
            volume_multiplier = 1.08
            if any(symbol in instrument_key for symbol in ("RELIANCE", "ICICIBANK", "HDFCBANK")):
                drift = -1.8
                volume_multiplier = 1.35
            else:
                drift = math.sin(len(instrument_key)) * 0.6
            if "KOTAKBANK" in instrument_key:
                volume_multiplier = 1.25
            live_close = round(last.close + drift, 2)
            live_high = max(last.high, live_close + abs(drift) * 0.2)
            live_low = min(last.low, live_close - abs(drift) * 0.2)
            quotes[instrument_key] = QuoteSnapshot(
                instrument_key=instrument_key,
                last_price=live_close,
                live_open=last.open,
                live_high=round(live_high, 2),
                live_low=round(live_low, 2),
                live_close=live_close,
                live_volume=last.volume * volume_multiplier,
                prev_close=candles[-2].close,
                timestamp=now,
            )

        return quotes

    def get_historical_daily_candles(self, instrument_key: str, from_date: str, to_date: str) -> List[Candle]:
        random = Random(f"{self._seed}:{instrument_key}")
        start = datetime(2025, 10, 1)
        candles: List[Candle] = []
        price = 200 + random.random() * 1200
        trend_boost = 1.3 if any(symbol in instrument_key for symbol in ("RELIANCE", "ICICIBANK", "HDFCBANK")) else 0.5

        for index in range(140):
            timestamp = (start + timedelta(days=index)).date().isoformat()
            trend = math.sin(index / 11) * 1.5 + (0.3 if "NIFTY" in instrument_key else trend_boost)
            body = random.uniform(-1.8, 2.2) + trend
            open_price = max(20.0, price)
            close_price = max(20.0, open_price + body)
            high_price = max(open_price, close_price) + random.uniform(0.5, 2.4)
            low_price = min(open_price, close_price) - random.uniform(0.5, 2.1)
            volume = 500_000 + (index * 2_500) + random.uniform(0, 180_000)

            candles.append(
                Candle(
                    timestamp=timestamp,
                    open=round(open_price, 2),
                    high=round(high_price, 2),
                    low=round(low_price, 2),
                    close=round(close_price, 2),
                    volume=round(volume, 2),
                )
            )

            price = close_price + random.uniform(-0.8, 1.3)

        return candles

    def get_historical_intraday_candles(
        self, instrument_key: str, from_date: str, to_date: str, interval: str = "30minute"
    ) -> List[Candle]:
        """Generate sample intraday candles for testing"""
        random = Random(f"{self._seed}:{instrument_key}:intraday")
        candles: List[Candle] = []
        
        # Generate candles for today only (intraday)
        today = datetime.now().replace(hour=9, minute=15, second=0, microsecond=0)
        price = 200 + random.random() * 1200
        
        # Market hours: 9:15 AM to 3:30 PM
        minutes_map = {"1minute": 1, "30minute": 30}
        interval_minutes = minutes_map.get(interval, 30)
        
        current_time = today
        end_time = today.replace(hour=15, minute=30)
        
        while current_time <= end_time:
            trend = math.sin(current_time.hour / 3) * 0.8
            body = random.uniform(-0.5, 0.8) + trend
            open_price = max(20.0, price)
            close_price = max(20.0, open_price + body)
            high_price = max(open_price, close_price) + random.uniform(0.2, 1.0)
            low_price = min(open_price, close_price) - random.uniform(0.2, 0.8)
            volume = 50_000 + random.uniform(0, 30_000)
            
            candles.append(
                Candle(
                    timestamp=current_time.isoformat(),
                    open=round(open_price, 2),
                    high=round(high_price, 2),
                    low=round(low_price, 2),
                    close=round(close_price, 2),
                    volume=round(volume, 2),
                )
            )
            
            price = close_price + random.uniform(-0.3, 0.5)
            current_time += timedelta(minutes=interval_minutes)
        
        return candles
