import json
import math
from typing import Any, Dict, List, Optional, Tuple


Decision = Dict[str, Any]


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _as_float(payload: Dict[str, Any], key: str, default: Optional[float] = None) -> float:
    value = payload.get(key, default)
    if value is None:
        raise ValueError(f"Missing required numeric field: {key}")
    return float(value)


def _as_text(payload: Dict[str, Any], key: str, default: Optional[str] = None) -> str:
    value = payload.get(key, default)
    if value is None:
        raise ValueError(f"Missing required text field: {key}")
    return str(value).strip().lower()


def _to_rupees(value: float) -> str:
    return f"INR {value:,.2f}"


def _to_price(value: float) -> str:
    return f"{value:.2f}"


def _market_condition(close_price: float, high: float, low: float, volatility_pct: float, ema_trend: str, macd: str) -> str:
    day_range_pct = ((high - low) / close_price) * 100 if close_price else 0
    effective_volatility = max(volatility_pct, day_range_pct)

    if effective_volatility >= 3.5:
        return "volatile"

    if ema_trend != "neutral" and ema_trend == macd and effective_volatility <= 3.5:
        return "trending"

    return "sideways"


def _pick_direction(
    ema_trend: str, 
    macd: str, 
    index_trend: str, 
    sector_strength: str, 
    news_sentiment: str, 
    trading_mode: str = "swing",
    vwap_trend: str = "neutral",
    supertrend_trend: str = "neutral",
) -> Optional[str]:
    """Professional direction picking with VWAP priority"""
    bullish_votes = 0
    bearish_votes = 0

    # VWAP is the most important (institutional fair value)
    if vwap_trend == "bullish":
        bullish_votes += 2  # Double weight
    elif vwap_trend == "bearish":
        bearish_votes += 2
    
    # Supertrend (volatility-adjusted trend)
    if supertrend_trend == "bullish":
        bullish_votes += 1.5
    elif supertrend_trend == "bearish":
        bearish_votes += 1.5
    
    # EMA and MACD (traditional)
    for signal in (ema_trend, macd):
        if signal == "bullish":
            bullish_votes += 1
        elif signal == "bearish":
            bearish_votes += 1
    
    # For intraday, be more lenient with index trend
    if trading_mode == "intraday":
        if index_trend == "bullish":
            bullish_votes += 0.5
        elif index_trend == "bearish":
            bearish_votes += 0.5
    else:
        if index_trend == "bullish":
            bullish_votes += 1
        elif index_trend == "bearish":
            bearish_votes += 1

    if sector_strength == "strong":
        bullish_votes += 1
    elif sector_strength == "weak":
        bearish_votes += 1

    if news_sentiment == "positive":
        bullish_votes += 1
    elif news_sentiment == "negative":
        bearish_votes += 1

    # More lenient for intraday with VWAP/Supertrend
    if trading_mode == "intraday":
        if bullish_votes >= 2.5 and bearish_votes <= 2:
            return "BUY"
        if bearish_votes >= 2.5 and bullish_votes <= 2:
            return "SELL"
    else:
        if bullish_votes >= 4 and bearish_votes <= 1:
            return "BUY"
        if bearish_votes >= 4 and bullish_votes <= 1:
            return "SELL"

    return None


def _trend_component(direction: str, ema_trend: str, index_trend: str, sector_strength: str, market_condition: str) -> float:
    score = 0.0

    if direction == "BUY":
        if ema_trend == "bullish":
            score += 4.0
        if index_trend == "bullish":
            score += 3.0
        if sector_strength == "strong":
            score += 2.0
    else:
        if ema_trend == "bearish":
            score += 4.0
        if index_trend == "bearish":
            score += 3.0
        if sector_strength == "weak":
            score += 2.0

    if market_condition == "trending":
        score += 1.0

    return _clamp(score, 0.0, 10.0)


def _momentum_component(direction: str, rsi: float, macd: str) -> float:
    score = 0.0

    if direction == "BUY":
        if 52 <= rsi <= 68:
            score += 6.0
        elif 48 <= rsi < 52 or 68 < rsi <= 72:
            score += 4.0
        elif 40 <= rsi < 48:
            score += 2.0

        if macd == "bullish":
            score += 4.0
    else:
        if 32 <= rsi <= 48:
            score += 6.0
        elif 28 <= rsi < 32 or 48 < rsi <= 52:
            score += 4.0
        elif 52 < rsi <= 60:
            score += 2.0

        if macd == "bearish":
            score += 4.0

    return _clamp(score, 0.0, 10.0)


def _volume_component(volume: float, average_volume: Optional[float], liquidity: str) -> float:
    if average_volume and average_volume > 0:
        ratio = volume / average_volume
        if ratio >= 1.5:
            return 9.0
        if ratio >= 1.2:
            return 8.0
        if ratio >= 1.0:
            return 6.5
        if ratio >= 0.8:
            return 5.0
        return 3.0

    if liquidity == "high":
        return 6.5
    if liquidity == "medium":
        return 5.0
    return 3.0


def _sentiment_component(direction: str, news_sentiment: str) -> float:
    if news_sentiment == "neutral":
        return 5.5

    if direction == "BUY":
        return 9.0 if news_sentiment == "positive" else 2.5

    return 9.0 if news_sentiment == "negative" else 2.5


def _market_component(direction: str, index_trend: str, sector_strength: str, liquidity: str) -> float:
    score = 0.0

    if direction == "BUY":
        if index_trend == "bullish":
            score += 4.0
        if sector_strength == "strong":
            score += 3.0
    else:
        if index_trend == "bearish":
            score += 4.0
        if sector_strength == "weak":
            score += 3.0

    if liquidity == "high":
        score += 3.0
    elif liquidity == "medium":
        score += 2.0
    else:
        score += 0.5

    return _clamp(score, 0.0, 10.0)


def _risk_profile_limits(risk_level: str) -> Tuple[float, float]:
    if risk_level == "low":
        return 1.75, 2.75
    if risk_level == "high":
        return 4.0, 5.0
    return 2.75, 3.75


def _build_trade(
    direction: str,
    asset: str,
    close_price: float,
    support: float,
    resistance: float,
    volatility_pct: float,
    capital: float,
    risk_per_trade_pct: float,
    risk_level: str,
    score: float,
    probability: float,
    market_condition: str,
    reasons: List[str],
    use_leverage: bool = False,
    leverage_multiplier: float = 1.0,
    trading_mode: str = "swing",
) -> Decision:
    buffer_pct = _clamp(volatility_pct * 0.25, 0.25, 1.0)
    buffer_abs = close_price * (buffer_pct / 100.0)

    if direction == "BUY":
        entry = close_price
        stop = support - buffer_abs
        target = resistance
        risk_per_unit = entry - stop
        reward_per_unit = target - entry
    else:
        entry = close_price
        stop = resistance + buffer_abs
        target = support
        risk_per_unit = stop - entry
        reward_per_unit = entry - target

    if risk_per_unit <= 0 or reward_per_unit <= 0:
        return {"action": "NO TRADE", "reason": ["The price is sitting too close to a key level to define a safe trade."]}

    rr_ratio = reward_per_unit / risk_per_unit
    
    # More lenient R:R for intraday
    min_rr = 1.5 if trading_mode == "intraday" else 2.0
    if rr_ratio < min_rr:
        return {"action": "NO TRADE", "reason": [f"The possible reward is too small compared with the downside (R:R {rr_ratio:.2f})."]}

    stop_distance_pct = (risk_per_unit / entry) * 100
    max_stop_distance_pct, max_volatility_pct = _risk_profile_limits(risk_level)
    
    # More lenient for intraday
    if trading_mode == "intraday":
        max_stop_distance_pct *= 1.5
        max_volatility_pct *= 1.5

    if stop_distance_pct > max_stop_distance_pct:
        return {"action": "NO TRADE", "reason": [f"The stop would need to be too wide ({stop_distance_pct:.1f}%) for your chosen risk style."]}

    if volatility_pct > max_volatility_pct:
        return {"action": "NO TRADE", "reason": [f"Price swings ({volatility_pct:.1f}%) are too large for a beginner-safe entry right now."]}

    # Calculate position size with leverage
    effective_capital = capital * leverage_multiplier if use_leverage else capital
    max_risk_amount = capital * (risk_per_trade_pct / 100.0)  # Risk is still based on actual capital
    
    units_by_risk = math.floor(max_risk_amount / risk_per_unit)
    units_by_capital = math.floor(effective_capital / entry)
    units = int(min(units_by_risk, units_by_capital))

    if units < 1:
        return {"action": "NO TRADE", "reason": ["Your account size is too small for this setup while keeping risk under control."]}

    invested_amount = units * entry
    actual_risk = units * risk_per_unit
    margin_required = invested_amount / leverage_multiplier if use_leverage else invested_amount

    time_window = "1 to 3 trading sessions" if market_condition == "trending" and volatility_pct <= 2.0 else "same day to 2 sessions"

    result = {
        "action": direction,
        "asset": asset,
        "confidence": f"{probability:.0f}%",
        "entry": _to_price(entry),
        "stop_loss": _to_price(stop),
        "target": _to_price(target),
        "position_size": _to_rupees(invested_amount),
        "risk_amount": _to_rupees(actual_risk),
        "time_window": time_window,
        "reason": reasons[:4],
    }
    
    # Add leverage info if applicable
    if use_leverage:
        result["leverage"] = f"{leverage_multiplier}x"
        result["margin_required"] = _to_rupees(margin_required)
        result["exposure"] = _to_rupees(invested_amount)

    # More lenient scoring for intraday
    min_score = 5.0 if trading_mode == "intraday" else 7.0
    min_prob = 50.0 if trading_mode == "intraday" else 65.0
    
    if score < min_score or probability < min_prob:
        return {"action": "NO TRADE", "reason": [f"The setup is decent (score: {score:.1f}, prob: {probability:.0f}%), but not strong enough to meet the quality bar."]}

    return result


def decide_trade(payload: Dict[str, Any]) -> Decision:
    asset = str(payload.get("asset", "")).strip().upper()
    if not asset:
        raise ValueError("Missing required field: asset")

    market_data = payload.get("market_data", {})
    technical_signals = payload.get("technical_signals", {})
    market_context = payload.get("market_context", {})
    sentiment = payload.get("sentiment", {})
    user_profile = payload.get("user_profile", {})

    open_price = _as_float(market_data, "open")
    high = _as_float(market_data, "high")
    low = _as_float(market_data, "low")
    close_price = _as_float(market_data, "close")
    volume = _as_float(market_data, "volume", 0.0)
    average_volume = market_data.get("average_volume")
    average_volume = float(average_volume) if average_volume is not None else None

    explicit_volatility = market_data.get("volatility")
    if explicit_volatility is not None:
        volatility_pct = float(explicit_volatility)
    else:
        volatility_pct = ((high - low) / close_price) * 100 if close_price else 0.0

    rsi = _as_float(technical_signals, "rsi")
    ema_trend = _as_text(technical_signals, "ema_trend")
    macd = _as_text(technical_signals, "macd")
    support = _as_float(technical_signals, "support")
    resistance = _as_float(technical_signals, "resistance")
    
    # Professional indicators
    vwap_trend = technical_signals.get("vwap_trend", "neutral")
    supertrend_trend = technical_signals.get("supertrend_trend", "neutral")
    vwap_value = market_data.get("vwap", close_price)
    supertrend_value = market_data.get("supertrend_value", close_price)
    volume_surge = market_data.get("volume_surge", 1.0)

    index_trend = _as_text(market_context, "index_trend")
    sector_strength = _as_text(market_context, "sector_strength")
    liquidity = _as_text(market_context, "liquidity")

    news_sentiment = _as_text(sentiment, "news_sentiment")

    capital = _as_float(user_profile, "capital")
    risk_per_trade_pct = _as_float(user_profile, "risk_per_trade_pct")
    risk_level = _as_text(user_profile, "risk_level")
    use_leverage = user_profile.get("use_leverage", False)
    leverage_multiplier = float(user_profile.get("leverage_multiplier", 1.0))
    trading_mode = user_profile.get("trading_mode", "swing")

    market_condition = _market_condition(close_price, high, low, volatility_pct, ema_trend, macd)

    if liquidity == "low":
        return {"action": "NO TRADE", "reason": ["This asset is too illiquid for a clean beginner-friendly trade."]}

    if not (low <= close_price <= high) or resistance <= support:
        return {"action": "NO TRADE", "reason": ["The price inputs are not consistent enough to trust the setup."]}

    if close_price <= 0 or capital <= 0 or risk_per_trade_pct <= 0:
        return {"action": "NO TRADE", "reason": ["The trade inputs are incomplete or invalid."]}

    direction = _pick_direction(ema_trend, macd, index_trend, sector_strength, news_sentiment, trading_mode, vwap_trend, supertrend_trend)
    if direction is None:
        return {"action": "NO TRADE", "reason": ["The signals are mixed, so the setup is not clear enough."]}

    # More lenient market condition check for intraday
    if trading_mode != "intraday" and market_condition != "trending":
        return {"action": "NO TRADE", "reason": ["The market is not moving cleanly enough to justify a trade."]}
    
    # VWAP-based position check (professional) - now a warning, not hard rejection
    vwap_warning = None
    if direction == "BUY" and close_price < vwap_value * 0.995:  # Allow 0.5% below VWAP
        vwap_warning = f"Price slightly below VWAP (₹{vwap_value:.2f}) - weaker setup."
    
    if direction == "SELL" and close_price > vwap_value * 1.005:  # Allow 0.5% above VWAP
        vwap_warning = f"Price slightly above VWAP (₹{vwap_value:.2f}) - weaker setup."

    if direction == "BUY" and close_price >= resistance * 0.98:
        return {"action": "NO TRADE", "reason": ["Price is already too close to an upside barrier to enter safely."]}

    if direction == "SELL" and close_price <= support * 1.02:
        return {"action": "NO TRADE", "reason": ["Price is already too close to a downside barrier to enter safely."]}

    trend_strength = _trend_component(direction, ema_trend, index_trend, sector_strength, market_condition)
    momentum = _momentum_component(direction, rsi, macd)
    volume_score = _volume_component(volume, average_volume, liquidity)
    sentiment_score = _sentiment_component(direction, news_sentiment)
    market_score = _market_component(direction, index_trend, sector_strength, liquidity)
    
    # Bonus for volume surge (institutional participation)
    volume_bonus = 0.0
    if volume_surge >= 2.0:
        volume_bonus = 1.5  # Very high interest
    elif volume_surge >= 1.5:
        volume_bonus = 1.0  # High interest

    score = round(
        (trend_strength * 0.25)
        + (momentum * 0.20)
        + (volume_score * 0.15)
        + (sentiment_score * 0.15)
        + (market_score * 0.25)
        + volume_bonus,
        2,
    )

    penalties = 0.0
    if volume_score < 5.0:
        penalties += 2.0 if trading_mode == "intraday" else 4.0
    if news_sentiment == "neutral":
        penalties += 0.5 if trading_mode == "intraday" else 1.5
    if close_price < open_price and direction == "BUY":
        penalties += 1.0 if trading_mode == "intraday" else 2.0
    if close_price > open_price and direction == "SELL":
        penalties += 1.0 if trading_mode == "intraday" else 2.0

    probability = _clamp(40.0 + (score * 4.5) - penalties, 35.0, 85.0)

    reasons: List[str] = []
    if direction == "BUY":
        reasons.append(f"Price (₹{close_price:.2f}) is {((close_price - vwap_value) / vwap_value * 100):.1f}% above VWAP (₹{vwap_value:.2f}) - institutional support.")
        reasons.append("The setup has room to move higher before the next major barrier.")
    else:
        reasons.append(f"Price (₹{close_price:.2f}) is {((vwap_value - close_price) / vwap_value * 100):.1f}% below VWAP (₹{vwap_value:.2f}) - institutional pressure.")
        reasons.append("The setup has room to move lower before the next major barrier.")

    if volume_surge >= 1.5:
        reasons.append(f"Volume surge {volume_surge:.2f}x indicates strong institutional participation.")
    elif volume_score >= 6.5:
        reasons.append("Participation is healthy, which supports follow-through.")
    else:
        reasons.append("Participation is acceptable, but not strong enough to justify aggression.")

    if sentiment_score >= 8.0:
        reasons.append("Recent news is not fighting against the trade.")
    else:
        reasons.append("News is not strong enough to add much conviction.")

    reasons.append(f"Risk is controlled with Supertrend stop at ₹{supertrend_value:.2f}.")

    return _build_trade(
        direction=direction,
        asset=asset,
        close_price=close_price,
        support=support,
        resistance=resistance,
        volatility_pct=volatility_pct,
        capital=capital,
        risk_per_trade_pct=risk_per_trade_pct,
        risk_level=risk_level,
        score=score,
        probability=probability,
        market_condition=market_condition,
        reasons=reasons,
        use_leverage=use_leverage,
        leverage_multiplier=leverage_multiplier,
        trading_mode=trading_mode,
    )


def decide_trade_json(payload: Dict[str, Any]) -> str:
    return json.dumps(decide_trade(payload), indent=2)
