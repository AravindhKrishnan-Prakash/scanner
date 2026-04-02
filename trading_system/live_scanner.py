from __future__ import annotations

from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .config import RuntimeConfig
from .decision_engine import decide_trade
from .email_notifier import EmailNotifier
from .indicators import (
    adx,
    atr,
    average_volume,
    classify_liquidity,
    ema,
    macd,
    percent_volatility,
    relative_strength,
    resistance_level,
    rsi,
    support_level,
    vwap,
    supertrend,
    volume_surge_ratio,
    opening_range_breakout,
)
from .live_models import Candle, QuoteSnapshot, ResolvedInstrument


try:
    INDIA_TZ = ZoneInfo("Asia/Kolkata")
except ZoneInfoNotFoundError:
    INDIA_TZ = timezone(timedelta(hours=5, minutes=30))


class LiveScannerService:
    def __init__(self, provider, config: RuntimeConfig) -> None:
        self.provider = provider
        self.config = config
        self._lock = Lock()
        self._resolved_watchlist: List[ResolvedInstrument] = []
        self._resolved_index: Optional[ResolvedInstrument] = None
        self._historical_cache: Dict[str, List[Candle]] = {}
        self._snapshot = {
            "mode": "booting",
            "provider": getattr(provider, "name", "unknown"),
            "status": "starting",
            "last_scan_at": None,
            "market": {},
            "opportunities": [],
            "watchlist": [],
            "errors": [],
        }
        self._email_notifier = EmailNotifier()

    @property
    def snapshot(self) -> dict:
        with self._lock:
            return dict(self._snapshot)

    def bootstrap(self) -> None:
        self._resolved_index = self.provider.resolve_query(self.config.market_index_query, prefer_equity=False)
        self._resolved_watchlist = [self.provider.resolve_query(item.query) for item in self.config.watchlist]
        self._warm_historical_cache(force=True)

    def run_scan(self) -> dict:
        if not self._resolved_index or not self._resolved_watchlist:
            self.bootstrap()

        self._warm_historical_cache(force=False)
        now = datetime.now(INDIA_TZ)
        all_instruments = [self._resolved_index, *self._resolved_watchlist]
        quotes = self.provider.get_bulk_quotes([item.instrument_key for item in all_instruments], interval="1d")
        index_candles = self._merged_candles(self._resolved_index, quotes)
        index_trend = self._index_trend(index_candles)

        opportunities: List[dict] = []
        watchlist_status: List[dict] = []
        errors: List[str] = []

        for instrument in self._resolved_watchlist:
            try:
                merged_candles = self._merged_candles(instrument, quotes)
                analysis = self._analyze_instrument(instrument, merged_candles, index_candles, index_trend)
                watchlist_status.append(analysis["summary"])
                if analysis["trade"] and analysis["trade"]["action"] != "NO TRADE":
                    opportunities.append(analysis["trade"])
            except Exception as exc:
                errors.append(f"{instrument.symbol}: {exc}")

        opportunities.sort(
            key=lambda item: (
                int(str(item.get("confidence", "0%")).rstrip("%") or "0"),
                item.get("asset", ""),
            ),
            reverse=True,
        )

        snapshot = {
            "mode": "live" if self.provider.name == "upstox" else "sample",
            "provider": self.provider.name,
            "status": "running",
            "trading_mode": self.config.scanner.trading_mode,
            "use_leverage": self.config.user_profile.use_leverage,
            "leverage_multiplier": self.config.user_profile.leverage_multiplier if self.config.user_profile.use_leverage else 1,
            "last_scan_at": now.isoformat(),
            "market": {
                "index": self._resolved_index.symbol if self._resolved_index else self.config.market_index_query,
                "trend": index_trend,
                "watched_symbols": len(self._resolved_watchlist),
                "qualified_trades": len(opportunities),
            },
            "opportunities": opportunities,
            "watchlist": watchlist_status,
            "errors": errors,
        }

        with self._lock:
            self._snapshot = snapshot
        
        # Send email notification if there are new opportunities
        if opportunities:
            self._email_notifier.send_trade_alert(opportunities)

        return snapshot

    def _warm_historical_cache(self, force: bool) -> None:
        today = datetime.now(INDIA_TZ).date()
        
        # For intraday mode, fetch intraday candles
        if self.config.scanner.trading_mode == "intraday":
            # For 30-minute candles: 13 candles per day (9:15 AM - 3:30 PM)
            # Need 60 candles minimum = ~5 days
            # Fetch more to be safe (10 days)
            from_date = (today - timedelta(days=10)).isoformat()
            to_date = today.isoformat()
            interval = self.config.scanner.intraday_candle_interval
            
            targets = [self._resolved_index, *self._resolved_watchlist]
            for instrument in targets:
                if instrument is None:
                    continue
                if not force and instrument.instrument_key in self._historical_cache:
                    continue
                
                # Check if provider supports intraday candles
                if hasattr(self.provider, 'get_historical_intraday_candles'):
                    self._historical_cache[instrument.instrument_key] = self.provider.get_historical_intraday_candles(
                        instrument.instrument_key,
                        from_date,
                        to_date,
                        interval,
                    )
                else:
                    # Fallback to daily candles
                    self._historical_cache[instrument.instrument_key] = self.provider.get_historical_daily_candles(
                        instrument.instrument_key,
                        from_date,
                        to_date,
                    )
        else:
            # Original swing trading logic
            from_date = (today - timedelta(days=self.config.scanner.history_days)).isoformat()
            to_date = today.isoformat()

            targets = [self._resolved_index, *self._resolved_watchlist]

            for instrument in targets:
                if instrument is None:
                    continue
                if not force and instrument.instrument_key in self._historical_cache:
                    continue
                self._historical_cache[instrument.instrument_key] = self.provider.get_historical_daily_candles(
                    instrument.instrument_key,
                    from_date,
                    to_date,
                )

    def _merged_candles(self, instrument: ResolvedInstrument, quotes: Dict[str, QuoteSnapshot]) -> List[Candle]:
        candles = list(self._historical_cache.get(instrument.instrument_key, []))
        quote = quotes.get(instrument.instrument_key)

        if not quote:
            return candles

        live_candle = Candle(
            timestamp=quote.timestamp or datetime.now(INDIA_TZ).isoformat(),
            open=quote.live_open or quote.prev_close or quote.last_price,
            high=quote.live_high or quote.last_price,
            low=quote.live_low or quote.last_price,
            close=quote.live_close or quote.last_price,
            volume=quote.live_volume,
        )

        if candles and candles[-1].timestamp[:10] == live_candle.timestamp[:10]:
            candles[-1] = live_candle
        else:
            candles.append(live_candle)

        return candles

    def _index_trend(self, candles: List[Candle]) -> str:
        closes = [candle.close for candle in candles]
        if len(closes) < 50:
            return "neutral"

        ema20 = ema(closes, 20)[-1]
        ema50 = ema(closes, 50)[-1]

        if ema20 > ema50:
            return "bullish"
        if ema20 < ema50:
            return "bearish"
        return "neutral"

    def _analyze_instrument(
        self,
        instrument: ResolvedInstrument,
        candles: List[Candle],
        index_candles: List[Candle],
        index_trend: str,
    ) -> dict:
        # For intraday mode, we need fewer candles (30min candles = 13 per day)
        # For swing mode, we need more (daily candles)
        min_candles = 30 if self.config.scanner.trading_mode == "intraday" else 60
        
        if len(candles) < min_candles:
            raise ValueError(f"Not enough history to calculate the full indicator set. Got {len(candles)} candles, need {min_candles}.")

        closes = [candle.close for candle in candles]
        last_candle = candles[-1]
        
        # Use shorter periods for intraday
        if self.config.scanner.trading_mode == "intraday":
            ema_short = 9
            ema_long = 21
        else:
            ema_short = 20
            ema_long = 50
            
        ema_short_val = ema(closes, ema_short)[-1]
        ema_long_val = ema(closes, ema_long)[-1]
        
        # PROFESSIONAL INDICATORS
        vwap_value = vwap(candles)
        supertrend_data = supertrend(candles, period=7, multiplier=3.0)
        volume_surge = volume_surge_ratio(candles, period=20)
        orb_data = opening_range_breakout(candles, range_minutes=3)  # 3 candles = ~90 min for 30min candles
        
        # Traditional indicators
        rsi_value = rsi(closes, 14)
        macd_values = macd(closes)
        atr_value = atr(candles, 14)
        adx_value = adx(candles, 14)
        avg_volume = average_volume(candles, min(20, len(candles) - 1))
        volume_ratio = (last_candle.volume / avg_volume) if avg_volume else 0.0
        support = support_level(candles[:-1], min(self.config.scanner.support_resistance_lookback, len(candles) - 1))
        resistance = resistance_level(candles[:-1], min(self.config.scanner.support_resistance_lookback, len(candles) - 1))
        
        # For relative strength, use available candles
        rs_period = min(20, len(candles) - 1, len(index_candles) - 1)
        relative_strength_value = relative_strength(closes, [candle.close for candle in index_candles], rs_period)
        liquidity = classify_liquidity(last_candle.close, avg_volume)
        volatility = percent_volatility(last_candle.close, atr_value)

        # PROFESSIONAL TREND DETERMINATION
        # Primary: VWAP (institutional fair value)
        vwap_trend = "bullish" if last_candle.close > vwap_value else "bearish" if last_candle.close < vwap_value else "neutral"
        
        # Secondary: Supertrend (volatility-adjusted)
        supertrend_trend = supertrend_data["direction"]
        
        # Tertiary: EMA (traditional)
        ema_trend = "bullish" if ema_short_val > ema_long_val else "bearish" if ema_short_val < ema_long_val else "neutral"
        
        # MACD confirmation
        macd_trend = "bullish" if macd_values["histogram"] > 0 else "bearish" if macd_values["histogram"] < 0 else "neutral"
        
        # Sector strength
        sector_strength = "strong" if relative_strength_value > 0 else "weak" if relative_strength_value < 0 else "neutral"

        # PROFESSIONAL FILTERS
        manual_filters: List[str] = []
        
        # Filter 1: Trend strength (ADX)
        if adx_value < self.config.scanner.minimum_adx:
            manual_filters.append(f"Trend strength too weak (ADX {adx_value:.1f} < {self.config.scanner.minimum_adx}).")
        
        # Filter 2: Volume surge (institutional participation)
        if volume_surge < self.config.scanner.minimum_volume_ratio:
            manual_filters.append(f"Volume too low (surge {volume_surge:.2f}x < {self.config.scanner.minimum_volume_ratio}x).")
        
        # Filter 3: VWAP and Supertrend alignment (for intraday)
        if self.config.scanner.trading_mode == "intraday":
            if vwap_trend != supertrend_trend and vwap_trend != "neutral" and supertrend_trend != "neutral":
                manual_filters.append(f"VWAP ({vwap_trend}) and Supertrend ({supertrend_trend}) not aligned.")
        
        # Filter 4: Session timing (avoid bad windows)
        current_time = datetime.now(INDIA_TZ)
        hour = current_time.hour
        minute = current_time.minute
        
        # Avoid opening chaos (9:15-9:25) - reduced from 9:30
        if hour == 9 and minute < 25:
            manual_filters.append("Opening chaos window (9:15-9:25) - avoid trading.")
        
        # Avoid midday lull (12:00-13:00) - reduced window
        if hour == 12:
            manual_filters.append("Midday lull (12:00-13:00) - low institutional volume.")
        
        # Force exit after 15:00 (3:00 PM) - extended from 14:30
        if hour >= 15:
            manual_filters.append("Squaring off time (after 15:00) - no new entries.")

        payload = {
            "asset": instrument.symbol,
            "market_data": {
                "open": last_candle.open,
                "high": last_candle.high,
                "low": last_candle.low,
                "close": last_candle.close,
                "volume": last_candle.volume,
                "average_volume": avg_volume,
                "volatility": volatility,
                "vwap": vwap_value,
                "supertrend_value": supertrend_data["value"],
                "volume_surge": volume_surge,
            },
            "technical_signals": {
                "rsi": rsi_value,
                "ema_trend": ema_trend,
                "macd": macd_trend,
                "vwap_trend": vwap_trend,
                "supertrend_trend": supertrend_trend,
                "support": support,
                "resistance": resistance,
                "orb_breakout": orb_data["breakout"],
                "orb_direction": orb_data["direction"],
            },
            "market_context": {
                "index_trend": index_trend,
                "sector_strength": sector_strength,
                "liquidity": liquidity,
            },
            "sentiment": {
                "news_sentiment": "neutral"
            },
            "user_profile": {
                "capital": self.config.user_profile.capital,
                "risk_per_trade_pct": self.config.user_profile.risk_per_trade_pct,
                "risk_level": self.config.user_profile.risk_level,
                "use_leverage": self.config.user_profile.use_leverage,
                "leverage_multiplier": self.config.user_profile.leverage_multiplier,
                "trading_mode": self.config.scanner.trading_mode,
            },
        }

        trade = {"action": "NO TRADE", "reason": manual_filters} if manual_filters else decide_trade(payload)

        summary = {
            "symbol": instrument.symbol,
            "price": f"{last_candle.close:.2f}",
            "trend": vwap_trend,  # Use VWAP trend as primary
            "index_trend": index_trend,
            "adx": round(adx_value, 1),
            "rsi": round(rsi_value, 1),
            "volume_ratio": round(volume_surge, 2),  # Use volume surge
            "status": trade["action"],
            "vwap": f"{vwap_value:.2f}",
            "supertrend": supertrend_trend,
        }

        if trade["action"] != "NO TRADE":
            trade["instrument_key"] = instrument.instrument_key
            trade["market_view"] = {
                "index_trend": index_trend,
                "relative_strength": round(relative_strength_value, 4),
                "adx": round(adx_value, 1),
                "volume_surge": round(volume_surge, 2),
                "vwap": round(vwap_value, 2),
                "vwap_distance_pct": round(((last_candle.close - vwap_value) / vwap_value) * 100, 2),
                "supertrend": supertrend_trend,
                "supertrend_value": round(supertrend_data["value"], 2),
            }
        elif not trade.get("reason"):
            trade["reason"] = ["The setup does not meet the professional scanner quality filters."]

        return {"summary": summary, "trade": trade}
