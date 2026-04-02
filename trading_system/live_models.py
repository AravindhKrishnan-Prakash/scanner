from dataclasses import dataclass
from typing import Optional


@dataclass
class Candle:
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class ResolvedInstrument:
    query: str
    symbol: str
    instrument_key: str
    name: Optional[str] = None


@dataclass
class QuoteSnapshot:
    instrument_key: str
    last_price: float
    live_open: float
    live_high: float
    live_low: float
    live_close: float
    live_volume: float
    prev_close: float
    timestamp: str
