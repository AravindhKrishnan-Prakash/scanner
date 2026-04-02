# Intraday Trading Guide

## 🎯 Your System is Now Ready for Intraday Trading!

I've upgraded your trading scanner to support intraday trading with leverage. Here's everything you need to know:

---

## ✅ What Changed

### 1. Configuration (config/watchlist.json)
- **Trading Mode:** Changed from "swing" to "intraday"
- **Leverage:** Enabled with 5x multiplier (MIS margin)
- **Scan Speed:** Faster (15 seconds instead of 30)
- **Candle Interval:** Using 30-minute candles (Upstox limitation: only 1min or 30min available)
- **Stricter Filters:** ADX > 20, Volume ratio > 1.2

### 2. Backend Updates
- Added intraday candle support (5min, 15min, 30min)
- Leverage calculations in decision engine
- Position sizing with margin requirements
- Time-aware scanning for market hours

### 3. UI Enhancements
- Shows trading mode (Intraday/Swing)
- Displays leverage multiplier
- Shows margin required vs total exposure
- Orange leverage badge on opportunity cards

---

## 🚀 How to Use

### Step 1: Start the Scanner
```bash
.venv\Scripts\python dashboard_server.py
```

### Step 2: Open Dashboard
Go to: http://127.0.0.1:8010

### Step 3: Watch for Signals
The scanner will:
- Scan every 15 seconds
- Use 30-minute candles (Upstox only supports 1min or 30min)
- Show only high-quality setups
- Calculate leverage positions automatically

---

## 📊 Understanding the Signals

### Opportunity Card Shows:
1. **Action:** BUY or SELL
2. **Confidence:** 65-85% (quality score)
3. **Leverage Badge:** "5X LEVERAGE" (if enabled)
4. **Entry Price:** Where to enter
5. **Stop Loss:** Where to exit if wrong
6. **Target:** Profit target
7. **Position Size:** Total exposure (with leverage)
8. **Margin Required:** Actual capital needed
9. **Risk Amount:** Maximum loss if stop hit
10. **Time Window:** Expected holding period

### Example:
```
BUY - RELIANCE - 75% Confidence
5X LEVERAGE

Entry: 2,450.00
Stop: 2,430.00
Target: 2,490.00

Position Size: INR 2,45,000 (total exposure)
Margin Required: INR 49,000 (20% of exposure)
Risk: INR 2,000 (if stop hit)

Time Window: same day to 2 sessions
```

---

## 💰 Leverage Explained

### What is 5x Leverage?
- You control ₹5 worth of stock for every ₹1 you have
- Example: ₹1,00,000 capital = ₹5,00,000 buying power

### How It Works:
- **Without Leverage:** Buy 100 shares @ ₹1,000 = ₹1,00,000 needed
- **With 5x Leverage:** Buy 500 shares @ ₹1,000 = ₹1,00,000 margin needed (₹5,00,000 exposure)

### Risk:
- **1% move in your favor:** 5% profit on capital
- **1% move against you:** 5% loss on capital
- **Always use stop losses!**

---

## ⚙️ Configuration Options

Edit `config/watchlist.json` to customize:

### Trading Mode
```json
"trading_mode": "intraday"  // or "swing"
```

### Leverage Settings
```json
"use_leverage": true,
"leverage_multiplier": 5  // 5x to 20x typical for MIS
```

### Candle Interval
```json
"intraday_candle_interval": "30minute"  // "1minute" or "30minute" (Upstox limitation)
```

**Note:** Upstox API only supports 1-minute and 30-minute intraday candles. We use 30-minute for better signal quality and less noise.

### Scan Speed
```json
"poll_seconds": 15  // How often to scan (seconds)
```

### Exit Time
```json
"intraday_exit_time": "15:15"  // Square off before this time
```

### Filter Strength
```json
"minimum_adx": 20,  // Trend strength (higher = stricter)
"minimum_volume_ratio": 1.2  // Volume participation (higher = stricter)
```

---

## 🎯 Best Practices for Intraday

### 1. Timing
- Start scanning after 9:30 AM (avoid opening volatility)
- Best signals: 10:00 AM - 2:30 PM
- Square off all positions by 3:15 PM

### 2. Risk Management
- Never risk more than 1-2% per trade
- Always use stop losses
- Don't overtrade - quality over quantity
- With 5x leverage, a 1% stop = 5% capital risk

### 3. Signal Quality
- Wait for 65%+ confidence signals
- Check NIFTY trend alignment
- Look for volume confirmation
- Avoid trading against index trend

### 4. Position Sizing
- The system calculates this automatically
- Margin required = what you need in account
- Exposure = total position value
- Risk amount = max loss if stop hit

---

## 🔄 Switching Between Modes

### For Intraday Trading:
```json
{
  "scanner": {
    "trading_mode": "intraday",
    "intraday_candle_interval": "30minute",
    "poll_seconds": 15,
    "minimum_adx": 20,
    "minimum_volume_ratio": 1.2
  },
  "user_profile": {
    "use_leverage": true,
    "leverage_multiplier": 5
  }
}
```

**Note:** Use "1minute" for very fast scalping (more noise) or "30minute" for cleaner signals (recommended).

### For Swing Trading:
```json
{
  "scanner": {
    "trading_mode": "swing",
    "poll_seconds": 30,
    "history_days": 120,
    "minimum_adx": 18,
    "minimum_volume_ratio": 1.05
  },
  "user_profile": {
    "use_leverage": false,
    "leverage_multiplier": 1
  }
}
```

---

## ⚠️ Important Warnings

### 1. This is Analysis Only
- The system does NOT place trades automatically
- You must manually execute trades on Upstox/broker
- Always verify signals before trading

### 2. Leverage Risks
- Leverage amplifies both profits AND losses
- A small move against you = big loss
- Never trade without stop losses
- Start with lower leverage (2x-3x) until experienced

### 3. Market Hours
- Intraday mode works best during market hours
- After hours, data may be stale
- Always square off before 3:15 PM

### 4. Capital Requirements
- Ensure you have sufficient margin
- Keep buffer for volatility
- Don't use 100% of capital

---

## 📈 Expected Results

### Conservative Settings (Current):
- 0-3 signals per day
- High quality setups only
- 65-85% confidence range
- Clear risk/reward (2:1 minimum)

### If You Want More Signals:
Lower the filters in config:
```json
"minimum_adx": 15,  // From 20
"minimum_volume_ratio": 1.0  // From 1.2
```

But remember: More signals ≠ Better results

---

## 🆘 Troubleshooting

### No Signals Showing?
- Normal! System is very selective
- Try during active market hours (10 AM - 2 PM)
- Check if NIFTY trend is clear (not sideways)
- Lower filters if needed (but carefully)

### Scanner Running Slow?
- Reduce watchlist size (fewer stocks)
- Increase poll_seconds (20-30)
- Check internet connection

### Leverage Not Showing?
- Verify `use_leverage: true` in config
- Restart the scanner
- Check browser console for errors

---

## 🎓 Learning Resources

### Understanding Indicators:
- **EMA:** Trend direction (20 above 50 = bullish)
- **RSI:** Overbought/oversold (30-70 range)
- **MACD:** Momentum confirmation
- **ADX:** Trend strength (>20 = strong)
- **Volume Ratio:** Participation (>1.2 = good)

### Risk Management:
- 1% risk per trade = safe
- 2% risk per trade = moderate
- 3%+ risk per trade = aggressive (not recommended)

---

## 📞 Next Steps

1. **Test in Sample Mode First**
   - Run without Upstox token
   - Understand the UI
   - Practice reading signals

2. **Paper Trade**
   - Note signals but don't trade
   - Track results for 1-2 weeks
   - Build confidence

3. **Start Small**
   - Use minimum capital
   - Lower leverage (2x-3x)
   - 1-2 trades per day max

4. **Scale Gradually**
   - Increase capital slowly
   - Add more stocks to watchlist
   - Optimize settings based on results

---

## 🎉 You're Ready!

Your intraday scanner is configured and ready to go. Remember:
- Quality over quantity
- Always use stop losses
- Start small and scale up
- This is a tool, not a guarantee

Happy trading! 📊💰
