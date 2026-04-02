# India Live Trading Scanner

This project now has two layers:

- A strict trade-decision engine that returns beginner-friendly JSON
- A live dashboard that scans Indian symbols, calculates indicators, and highlights only stronger trade setups

## Trading Modes

The scanner supports two trading modes:

### 1. Intraday Trading (NEW!)
- Uses 1min/30min candles for faster signals (Upstox limitation)
- Supports leverage (MIS margin - typically 5x to 20x)
- Scans every 15 seconds for quick opportunities
- Time-aware: only trades during market hours
- Auto square-off reminder before 3:15 PM
- Tighter filters for intraday volatility

### 2. Swing Trading (Original)
- Uses daily candles for multi-day trends
- Conservative approach for 2-7 day holds
- Scans every 30 seconds
- No leverage by default

## What the live system does

- Resolves Indian symbols through Upstox search
- Pulls live OHLC quotes in bulk
- Pulls historical candles (intraday or daily based on mode)
- Calculates EMA trend, RSI, MACD, ATR, ADX, support, resistance, liquidity, and relative strength
- Filters weak setups before they reach the UI
- Shows only qualified opportunities on the dashboard
- Calculates position sizing with optional leverage support

There is no perfect indicator. This starter uses a safer combination:

- Trend: EMA 20 and EMA 50
- Momentum: RSI 14 and MACD
- Trend quality: ADX 14
- Risk control: ATR and support/resistance
- Participation: live volume versus average volume
- Market context: NIFTY trend plus stock relative strength

## Files that matter

- `dashboard_server.py` - live dashboard backend
- `trading_system/upstox_provider.py` - Upstox market data integration
- `trading_system/live_scanner.py` - scanning and opportunity filtering
- `trading_system/indicators.py` - indicator calculations
- `trading_system/decision_engine.py` - trade decision logic with leverage support
- `config/watchlist.json` - your India watchlist, risk config, and trading mode
- `web/` - dashboard UI

## Setup

1. Create `.env` from `.env.example`
2. Put your Upstox access token in `.env`
3. Edit `config/watchlist.json` with the symbols you want to scan

If you do not add a token, the app runs in sample mode so you can still test the UI.

## Configuration for Intraday Trading

Edit `config/watchlist.json`:

```json
{
  "user_profile": {
    "capital": 100000,
    "risk_per_trade_pct": 1,
    "risk_level": "low",
    "use_leverage": true,
    "leverage_multiplier": 5
  },
  "scanner": {
    "poll_seconds": 15,
    "history_days": 30,
    "minimum_adx": 20,
    "minimum_volume_ratio": 1.2,
    "trading_mode": "intraday",
    "intraday_candle_interval": "30minute",
    "intraday_exit_time": "15:15"
  }
}
```

### Configuration Options:

**user_profile:**
- `use_leverage`: true/false - Enable MIS leverage
- `leverage_multiplier`: 5-20 - Typical MIS margin (5x = 20% margin)

**scanner:**
- `trading_mode`: "intraday" or "swing"
- `intraday_candle_interval`: "1minute" or "30minute" (Upstox only supports these)
- `intraday_exit_time`: "15:15" - Square off time
- `poll_seconds`: 15 for intraday, 30 for swing

## Run the live dashboard

```bash
.venv\Scripts\python dashboard_server.py
```

Open:

```text
http://127.0.0.1:8010
```

## Run the original manual decision engine

```bash
python main.py examples/buy_candidate.json
python main.py examples/no_trade_candidate.json
```

## Important notes

### For Intraday Trading:
- This version uses intraday candles (1min or 30min) for faster signals
- Upstox API limitation: only 1-minute and 30-minute intervals supported
- 30-minute recommended for cleaner signals with less noise
- Leverage calculations show margin required vs total exposure
- Filters are stricter (ADX > 20, Volume ratio > 1.2)
- Best used during market hours (9:15 AM - 3:30 PM IST)
- Remember to square off positions before 3:15 PM

### For Swing Trading:
- Conservative and better suited for beginner-friendly swing-style trades
- Uses daily candles for multi-day trend analysis
- No leverage by default
- Refreshes continuously and surfaces only setups that pass scanner filters

## Leverage & Risk Warning

⚠️ **IMPORTANT:** Leverage amplifies both profits AND losses. With 5x leverage:
- You can control ₹5,00,000 worth of stock with ₹1,00,000 capital
- But a 1% move against you = 5% loss on your capital
- Always use stop losses and proper position sizing
- This is for analysis only - you must manually place trades
