from __future__ import annotations

from typing import Any, Dict, List, Optional

from .live_models import Candle, QuoteSnapshot, ResolvedInstrument


class UpstoxProvider:
    name = "upstox"

    def __init__(self, access_token: str) -> None:
        import upstox_client
        from upstox_client.api.history_api import HistoryApi
        from upstox_client.api.instruments_api import InstrumentsApi
        from upstox_client.api.market_quote_v3_api import MarketQuoteV3Api

        configuration = upstox_client.Configuration()
        configuration.access_token = access_token
        api_client = upstox_client.ApiClient(configuration)

        self._history_api = HistoryApi(api_client)
        self._instruments_api = InstrumentsApi(api_client)
        self._quote_api = MarketQuoteV3Api(api_client)

    def resolve_query(self, query: str, prefer_equity: bool = True) -> ResolvedInstrument:
        kwargs: Dict[str, Any] = {"records": 10}
        if prefer_equity:
            kwargs["exchanges"] = "NSE"
            kwargs["segments"] = "EQ"

        response = self._instruments_api.search_instrument(query, **kwargs)
        payload = response.to_dict() if hasattr(response, "to_dict") else response
        candidates = self._extract_search_candidates(payload)
        match = self._pick_best_candidate(query, candidates)

        if not match:
            raise ValueError(f"Could not resolve instrument for query: {query}")

        instrument_key = str(match.get("instrument_key") or match.get("instrumentKey") or "").strip()
        symbol = str(
            match.get("trading_symbol")
            or match.get("tradingSymbol")
            or match.get("short_name")
            or match.get("name")
            or query
        ).strip()

        if not instrument_key:
            raise ValueError(f"Resolved search result is missing instrument key for query: {query}")

        return ResolvedInstrument(
            query=query,
            symbol=symbol.upper().replace(" ", ""),
            instrument_key=instrument_key,
            name=str(match.get("name") or match.get("company_name") or symbol).strip(),
        )

    def get_bulk_quotes(self, instrument_keys: List[str], interval: str = "1d") -> Dict[str, QuoteSnapshot]:
        joined_keys = ",".join(instrument_keys)
        response = self._quote_api.get_market_quote_ohlc(interval, instrument_key=joined_keys)
        payload = response.to_dict() if hasattr(response, "to_dict") else response
        data = payload.get("data", {}) if isinstance(payload, dict) else {}
        quotes: Dict[str, QuoteSnapshot] = {}

        for instrument_key, raw in data.items():
            live = raw.get("live_ohlc") or {}
            previous = raw.get("prev_ohlc") or {}
            quotes[instrument_key] = QuoteSnapshot(
                instrument_key=instrument_key,
                last_price=float(raw.get("last_price") or live.get("close") or 0.0),
                live_open=float(live.get("open") or 0.0),
                live_high=float(live.get("high") or 0.0),
                live_low=float(live.get("low") or 0.0),
                live_close=float(live.get("close") or 0.0),
                live_volume=float(live.get("volume") or 0.0),
                prev_close=float(previous.get("close") or 0.0),
                timestamp=str(live.get("ts") or ""),
            )

        return quotes

    def get_historical_daily_candles(self, instrument_key: str, from_date: str, to_date: str) -> List[Candle]:
        response = self._history_api.get_historical_candle_data1(
            instrument_key,
            "day",
            to_date,
            from_date,
            "2.0",
        )
        payload = response.to_dict() if hasattr(response, "to_dict") else response
        candles_raw = ((payload.get("data") or {}).get("candles") or []) if isinstance(payload, dict) else []
        candles = [self._parse_candle(row) for row in candles_raw]
        candles.sort(key=lambda candle: candle.timestamp)
        return candles

    def get_historical_intraday_candles(
        self, instrument_key: str, from_date: str, to_date: str, interval: str = "30minute"
    ) -> List[Candle]:
        """
        Get intraday candles for intraday trading.
        interval: "1minute", "30minute" (Upstox only supports these two for intraday)
        """
        # Map our interval names to Upstox API format
        interval_map = {
            "1minute": "1minute",
            "5minute": "1minute",  # Fallback to 1minute
            "15minute": "30minute",  # Fallback to 30minute
            "30minute": "30minute",
        }
        upstox_interval = interval_map.get(interval, "30minute")
        
        response = self._history_api.get_historical_candle_data1(
            instrument_key,
            upstox_interval,
            to_date,
            from_date,
            "2.0",
        )
        payload = response.to_dict() if hasattr(response, "to_dict") else response
        candles_raw = ((payload.get("data") or {}).get("candles") or []) if isinstance(payload, dict) else []
        candles = [self._parse_candle(row) for row in candles_raw]
        candles.sort(key=lambda candle: candle.timestamp)
        return candles

    @staticmethod
    def _parse_candle(row: List[Any]) -> Candle:
        if len(row) < 6:
            raise ValueError("Historical candle row does not have the expected shape.")

        return Candle(
            timestamp=str(row[0]),
            open=float(row[1]),
            high=float(row[2]),
            low=float(row[3]),
            close=float(row[4]),
            volume=float(row[5]),
        )

    def _extract_search_candidates(self, payload: Any) -> List[Dict[str, Any]]:
        candidates: List[Dict[str, Any]] = []

        def visit(node: Any) -> None:
            if isinstance(node, dict):
                if any(key in node for key in ("instrument_key", "instrumentKey")):
                    candidates.append(node)
                for value in node.values():
                    visit(value)
            elif isinstance(node, list):
                for item in node:
                    visit(item)

        visit(payload)
        return candidates

    def _pick_best_candidate(self, query: str, candidates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        normalized = query.strip().upper().replace(" ", "")
        exact_match: Optional[Dict[str, Any]] = None

        for candidate in candidates:
            symbol = str(candidate.get("trading_symbol") or candidate.get("tradingSymbol") or "").upper().replace(" ", "")
            short_name = str(candidate.get("short_name") or "").upper().replace(" ", "")
            name = str(candidate.get("name") or candidate.get("company_name") or "").upper().replace(" ", "")

            if normalized in {symbol, short_name, name}:
                exact_match = candidate
                break

        return exact_match or (candidates[0] if candidates else None)
