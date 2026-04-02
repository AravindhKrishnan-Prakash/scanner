from __future__ import annotations

from statistics import mean
from typing import List, Sequence

from .live_models import Candle


def ema(values: Sequence[float], period: int) -> List[float]:
    if not values:
        return []

    multiplier = 2 / (period + 1)
    result: List[float] = [float(values[0])]

    for value in values[1:]:
        result.append((float(value) - result[-1]) * multiplier + result[-1])

    return result


def rsi(closes: Sequence[float], period: int = 14) -> float:
    if len(closes) < period + 1:
        return 50.0

    gains: List[float] = []
    losses: List[float] = []

    for previous, current in zip(closes[:-1], closes[1:]):
        change = current - previous
        gains.append(max(change, 0.0))
        losses.append(abs(min(change, 0.0)))

    avg_gain = mean(gains[:period])
    avg_loss = mean(losses[:period])

    for gain, loss in zip(gains[period:], losses[period:]):
        avg_gain = ((avg_gain * (period - 1)) + gain) / period
        avg_loss = ((avg_loss * (period - 1)) + loss) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def macd(closes: Sequence[float], fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    if len(closes) < slow + signal:
        return {"line": 0.0, "signal": 0.0, "histogram": 0.0}

    fast_ema = ema(closes, fast)
    slow_ema = ema(closes, slow)
    line = [fast_value - slow_value for fast_value, slow_value in zip(fast_ema, slow_ema)]
    signal_line = ema(line, signal)

    return {
        "line": line[-1],
        "signal": signal_line[-1],
        "histogram": line[-1] - signal_line[-1],
    }


def true_range(previous_close: float, candle: Candle) -> float:
    return max(
        candle.high - candle.low,
        abs(candle.high - previous_close),
        abs(candle.low - previous_close),
    )


def atr(candles: Sequence[Candle], period: int = 14) -> float:
    if len(candles) < period + 1:
        return 0.0

    ranges: List[float] = []

    for previous, current in zip(candles[:-1], candles[1:]):
        ranges.append(true_range(previous.close, current))

    if len(ranges) < period:
        return 0.0

    current_atr = mean(ranges[:period])
    for value in ranges[period:]:
        current_atr = ((current_atr * (period - 1)) + value) / period

    return current_atr


def adx(candles: Sequence[Candle], period: int = 14) -> float:
    if len(candles) < (period * 2) + 1:
        return 0.0

    plus_dm: List[float] = []
    minus_dm: List[float] = []
    true_ranges: List[float] = []

    for previous, current in zip(candles[:-1], candles[1:]):
        up_move = current.high - previous.high
        down_move = previous.low - current.low

        plus_dm.append(up_move if up_move > down_move and up_move > 0 else 0.0)
        minus_dm.append(down_move if down_move > up_move and down_move > 0 else 0.0)
        true_ranges.append(true_range(previous.close, current))

    tr14 = sum(true_ranges[:period])
    plus14 = sum(plus_dm[:period])
    minus14 = sum(minus_dm[:period])

    dx_values: List[float] = []

    for index in range(period, len(true_ranges)):
        if index > period:
            tr14 = tr14 - (tr14 / period) + true_ranges[index]
            plus14 = plus14 - (plus14 / period) + plus_dm[index]
            minus14 = minus14 - (minus14 / period) + minus_dm[index]

        if tr14 == 0:
            continue

        plus_di = (plus14 / tr14) * 100
        minus_di = (minus14 / tr14) * 100
        denominator = plus_di + minus_di
        if denominator == 0:
            dx_values.append(0.0)
        else:
            dx_values.append(abs(plus_di - minus_di) / denominator * 100)

    if len(dx_values) < period:
        return 0.0

    adx_value = mean(dx_values[:period])
    for value in dx_values[period:]:
        adx_value = ((adx_value * (period - 1)) + value) / period

    return adx_value


def average_volume(candles: Sequence[Candle], period: int = 20) -> float:
    if not candles:
        return 0.0

    window = candles[-period:] if len(candles) >= period else candles
    return mean(candle.volume for candle in window)


def support_level(candles: Sequence[Candle], lookback: int = 20) -> float:
    if not candles:
        return 0.0

    window = candles[-lookback:] if len(candles) >= lookback else candles
    return min(candle.low for candle in window)


def resistance_level(candles: Sequence[Candle], lookback: int = 20) -> float:
    if not candles:
        return 0.0

    window = candles[-lookback:] if len(candles) >= lookback else candles
    return max(candle.high for candle in window)


def relative_strength(stock_closes: Sequence[float], index_closes: Sequence[float], period: int = 20) -> float:
    if len(stock_closes) < period + 1 or len(index_closes) < period + 1:
        return 0.0

    stock_return = (stock_closes[-1] / stock_closes[-period - 1]) - 1
    index_return = (index_closes[-1] / index_closes[-period - 1]) - 1
    return stock_return - index_return


def classify_liquidity(price: float, avg_volume: float) -> str:
    turnover = price * avg_volume

    if turnover >= 100_000_000:
        return "high"
    if turnover >= 20_000_000:
        return "medium"
    return "low"


def percent_volatility(price: float, atr_value: float) -> float:
    if price <= 0:
        return 0.0
    return (atr_value / price) * 100


def vwap(candles: Sequence[Candle]) -> float:
    """Calculate Volume Weighted Average Price (VWAP)
    
    VWAP = Σ(Typical Price × Volume) / Σ(Volume)
    
    This represents institutional fair value and is the most important
    intraday indicator. Price above VWAP = bullish, below = bearish.
    """
    if not candles:
        return 0.0
    
    total_pv = 0.0
    total_volume = 0.0
    
    for candle in candles:
        typical_price = (candle.high + candle.low + candle.close) / 3
        total_pv += typical_price * candle.volume
        total_volume += candle.volume
    
    return total_pv / total_volume if total_volume > 0 else candles[-1].close


def supertrend(candles: Sequence[Candle], period: int = 7, multiplier: float = 3.0) -> dict:
    """Calculate Supertrend indicator
    
    Uses ATR to create dynamic support/resistance levels.
    Returns the supertrend value and direction (bullish/bearish).
    
    Settings: (7, 3) for sensitive intraday, (10, 2) for less noise
    """
    if len(candles) < period + 1:
        return {"value": candles[-1].close if candles else 0.0, "direction": "neutral"}
    
    atr_value = atr(candles, period)
    
    # Calculate basic bands
    hl_avg = (candles[-1].high + candles[-1].low) / 2
    upper_band = hl_avg + (multiplier * atr_value)
    lower_band = hl_avg - (multiplier * atr_value)
    
    # Determine trend
    close = candles[-1].close
    
    if close > upper_band:
        direction = "bullish"
        value = lower_band
    elif close < lower_band:
        direction = "bearish"
        value = upper_band
    else:
        # Use previous candle to determine
        if len(candles) >= 2:
            prev_close = candles[-2].close
            if prev_close > upper_band:
                direction = "bullish"
                value = lower_band
            else:
                direction = "bearish"
                value = upper_band
        else:
            direction = "neutral"
            value = hl_avg
    
    return {"value": value, "direction": direction}


def volume_surge_ratio(candles: Sequence[Candle], period: int = 20) -> float:
    """Calculate current volume vs average volume ratio
    
    This identifies "Volume Shockers" - stocks with institutional participation.
    Ratio > 1.5 = High institutional interest
    Ratio > 2.0 = Very high interest (momentum gainers)
    """
    if not candles or len(candles) < 2:
        return 1.0
    
    current_volume = candles[-1].volume
    avg_vol = average_volume(candles[:-1], period)
    
    return current_volume / avg_vol if avg_vol > 0 else 1.0


def opening_range_breakout(candles: Sequence[Candle], range_minutes: int = 15) -> dict:
    """Detect Opening Range Breakout (ORB)
    
    Identifies if price has broken above/below the first 15-minute range.
    This is a high-probability signal when combined with volume.
    """
    if len(candles) < range_minutes + 1:
        return {"breakout": False, "direction": "none", "range_high": 0.0, "range_low": 0.0}
    
    # First N candles form the opening range
    opening_candles = candles[:range_minutes]
    range_high = max(c.high for c in opening_candles)
    range_low = min(c.low for c in opening_candles)
    
    current_price = candles[-1].close
    
    if current_price > range_high:
        return {
            "breakout": True,
            "direction": "bullish",
            "range_high": range_high,
            "range_low": range_low
        }
    elif current_price < range_low:
        return {
            "breakout": True,
            "direction": "bearish",
            "range_high": range_high,
            "range_low": range_low
        }
    else:
        return {
            "breakout": False,
            "direction": "none",
            "range_high": range_high,
            "range_low": range_low
        }
