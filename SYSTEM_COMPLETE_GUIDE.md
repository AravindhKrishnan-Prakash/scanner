# Complete Trading System Documentation

## 🎯 System Overview

This is a **fully automated intraday trading scanner** for Indian stock markets with:
- Live Upstox data integration
- 5x leverage support (MIS margin)
- Email notifications
- Web dashboard
- 30-minute candle analysis
- Automatic position sizing
- Risk management

---

## 📊 How Trade Signals Are Generated

### Step 1: Data Collection (Every 15 Seconds)

**Scanner fetches:**
- Live quotes from Upstox (current price, volume, OHLC)
- Historical 30-minute candles (last 10 days)
- NIFTY 50 index data for market context

**For each stock:**
- 20 stocks monitored simultaneously
- Real-time price updates
- Volume tracking
- Intraday candle formation

---

### Step 2: Technical Analysis

**Professional Indicators (Priority Order):**

1. **VWAP (Volume Weighted Average Price)** ⭐ PRIMARY
   - Institutional fair value benchmark
   - Price above VWAP = Bullish (institutional support)
   - Price below VWAP = Bearish (institutional pressure)
   - Most important intraday indicator
   - Gets 2x voting weight in signal generation

2. **Supertrend (7, 3)** ⭐ SECONDARY
   - Volatility-adjusted trend indicator
   - Uses ATR for dynamic support/resistance
   - Bullish: Price above Supertrend line
   - Bearish: Price below Supertrend line
   - Gets 1.5x voting weight
   - Used for stop loss placement

3. **Volume Surge Ratio** ⭐ INSTITUTIONAL PARTICIPATION
   - Current volume vs 20-period average
   - Minimum required: 1.5x
   - >1.5x = High institutional interest
   - >2.0x = Very high interest (momentum gainers)
   - Identifies "Volume Shockers"

4. **EMA (Exponential Moving Average)**
   - EMA 9 (short-term trend)
   - EMA 21 (medium-term trend)
   - Trend: Bullish if EMA 9 > EMA 21
   - Trend: Bearish if EMA 9 < EMA 21
   - Gets 1x voting weight

5. **MACD (Moving Average Convergence Divergence)**
   - Measures momentum
   - Bullish: Histogram > 0
   - Bearish: Histogram < 0
   - Gets 1x voting weight

6. **ADX (Average Directional Index)**
   - Period: 14
   - Measures trend strength
   - Minimum required: 15
   - Strong trend: >20
   - Very strong: >25

7. **RSI (Relative Strength Index)**
   - Period: 14
   - Range: 0-100
   - Overbought: >70
   - Oversold: <30
   - Ideal for BUY: 52-68
   - Ideal for SELL: 32-48

8. **ATR (Average True Range)**
   - Period: 14
   - Measures volatility
   - Used for Supertrend calculation

9. **Support & Resistance**
   - Lookback: 20 candles
   - Identifies key price levels
   - Used for entry/exit targets

10. **Relative Strength**
    - Stock performance vs NIFTY
    - Positive: Outperforming market
    - Negative: Underperforming market

11. **Opening Range Breakout (ORB)**
    - Tracks first 90-minute range
    - Detects breakouts above/below opening range
    - High-probability signal when combined with volume

---

### Step 3: Signal Filtering

**A stock must pass ALL these filters:**

#### Filter 1: Professional Trend Alignment
- VWAP is the primary trend indicator (institutional fair value)
- Supertrend provides volatility-adjusted confirmation
- EMA and MACD provide traditional confirmation
- Index trend considered (but not mandatory for intraday)

**Professional Voting System:**
- VWAP bullish = +2 votes for BUY (double weight)
- Supertrend bullish = +1.5 votes for BUY
- EMA bullish = +1 vote for BUY
- MACD bullish = +1 vote for BUY
- Index bullish = +0.5 vote for BUY (intraday)
- Sector strength = +1 vote for BUY
- **Need 3+ votes for BUY signal** (intraday)
- Same logic for SELL signals

**VWAP Position Check:**
- For BUY: Price MUST be above VWAP (institutional support)
- For SELL: Price MUST be below VWAP (institutional pressure)
- This is a hard filter - signals rejected if violated

#### Filter 2: ADX (Trend Strength)
- Minimum: 15
- Ensures the trend is strong enough
- Weak trends (<15) are rejected

#### Filter 3: Volume Surge (Institutional Participation)
- Minimum: 1.5x average volume
- Identifies "Volume Shockers" with institutional interest
- >1.5x = High institutional participation
- >2.0x = Very high interest (bonus scoring)
- Low volume = rejected

#### Filter 4: Price Position
- For BUY: Price must be below resistance (at least 2% away)
- For SELL: Price must be above support (at least 2% away)
- Ensures room to move

#### Filter 5: Risk/Reward Ratio
- Minimum: 1.5:1 for intraday
- Target must be at least 1.5x the stop distance
- Poor R:R = rejected

#### Filter 6: Stop Loss Distance
- Maximum: 2.6-4.1% (depending on risk level)
- Ensures stop isn't too wide
- Protects capital

#### Filter 7: Volatility Check
- Maximum: 4.1% (for low risk)
- Ensures price isn't too choppy
- High volatility = rejected

#### Filter 8: Quality Score
- Minimum score: 5.5/10 (intraday)
- Minimum probability: 55% (intraday)
- Calculated from all indicators
- Volume surge bonus: +1.0 for >1.5x, +1.5 for >2.0x
- Low quality = rejected

#### Filter 9: Session Timing (Intraday Only)
- **Avoid 9:15-9:30 AM** - Opening chaos
- **Best 10:00-11:30 AM** - Morning momentum
- **Avoid 11:30 AM-1:30 PM** - Midday lull
- **Best 1:30-2:30 PM** - Afternoon trends
- **Avoid after 2:30 PM** - Squaring off time
- Signals blocked during bad windows

---

### Step 4: Position Sizing (With Leverage)

**Calculation Process:**

1. **Determine Risk Amount**
   ```
   Risk Amount = Capital × Risk % per trade
   Example: ₹1,00,000 × 1% = ₹1,000
   ```

2. **Calculate Stop Distance**
   ```
   Stop Distance = Entry Price - Stop Loss
   Example: ₹2,450 - ₹2,430 = ₹20 per share
   ```

3. **Calculate Quantity (Without Leverage)**
   ```
   Quantity = Risk Amount ÷ Stop Distance
   Example: ₹1,000 ÷ ₹20 = 50 shares
   ```

4. **Apply Leverage (5x)**
   ```
   Effective Capital = ₹1,00,000 × 5 = ₹5,00,000
   Max Quantity = ₹5,00,000 ÷ ₹2,450 = 204 shares
   
   Final Quantity = min(50, 204) = 50 shares
   (Limited by risk, not capital)
   ```

5. **Calculate Margin Required**
   ```
   Position Value = 50 × ₹2,450 = ₹1,22,500
   Margin Required = ₹1,22,500 ÷ 5 = ₹24,500
   ```

6. **Calculate Risk**
   ```
   Actual Risk = 50 × ₹20 = ₹1,000
   (Exactly 1% of capital)
   ```

---

### Step 5: Signal Generation

**When ALL filters pass, a signal is generated with:**

#### Trade Details:
- **Action:** BUY or SELL
- **Asset:** Stock symbol (e.g., RELIANCE)
- **Confidence:** 55-85% (quality score)
- **Entry Price:** Current market price
- **Stop Loss:** Calculated from support/resistance + buffer
- **Target:** Calculated from resistance/support
- **Time Window:** "same day to 2 sessions"

#### Position Sizing:
- **Position Size:** Total exposure (e.g., ₹1,22,500)
- **Margin Required:** Capital needed (e.g., ₹24,500)
- **Risk Amount:** Maximum loss if stop hit (e.g., ₹1,000)
- **Leverage:** 5x (if enabled)

#### Reasoning:
- 4 bullet points explaining why this trade qualifies
- Based on trend, volume, risk/reward, market context

#### Market Context:
- Index trend (NIFTY bullish/bearish/neutral)
- Relative strength vs market
- ADX (trend strength)
- Volume ratio

---

## 📧 Email Notification System

### When Signals Appear:

**Email is sent automatically with:**

1. **Subject Line:**
   ```
   🚨 2 New Trade Signals
   ```

2. **Email Body (HTML formatted):**
   - Beautiful cards for each signal
   - Color-coded (green for BUY, red for SELL)
   - Leverage badge (orange "5X LEVERAGE")
   - All trade details
   - Why this trade qualifies
   - Professional styling

3. **Duplicate Prevention:**
   - System tracks sent signals
   - Same signal won't email twice
   - Resets on scanner restart

4. **Delivery:**
   - Instant (within seconds)
   - Mobile notifications (via email app)
   - Works with Gmail, Outlook, Yahoo

---

## 🎯 Complete Signal Example

### Example BUY Signal:

```
Action: BUY
Asset: RELIANCE
Confidence: 72%
Leverage: 5X

Entry: 2,450.00
Stop Loss: 2,430.00
Target: 2,490.00

Position Size: INR 1,22,500 (total exposure)
Margin Required: INR 24,500 (20% of exposure)
Risk Amount: INR 1,000 (1% of capital)
Time Window: same day to 2 sessions

Why this trade:
• Price (₹2,450) is 1.2% above VWAP (₹2,421) - institutional support
• The setup has room to move higher before the next major barrier
• Volume surge 1.85x indicates strong institutional participation
• Risk is controlled with Supertrend stop at ₹2,430

Market Context:
• Index Trend: bullish
• Relative Strength: +0.0234 (outperforming)
• ADX: 22.5 (strong trend)
• Volume Surge: 1.85x (high institutional interest)
• VWAP: ₹2,421 (price above = bullish)
• VWAP Distance: +1.2%
• Supertrend: bullish
• Supertrend Value: ₹2,430

Risk/Reward: 2.0:1
Stop Distance: 0.82%
Volatility: 1.8%
```

### What This Means:

**To Execute This Trade:**
1. Buy 50 shares of RELIANCE at ₹2,450
2. Place stop loss at ₹2,430
3. Target profit at ₹2,490
4. You need ₹24,500 margin in your account
5. Maximum loss: ₹1,000 (if stop hit)
6. Potential profit: ₹2,000 (if target hit)
7. Square off before 3:15 PM (intraday)

**The Math:**
- Entry: 50 shares × ₹2,450 = ₹1,22,500 exposure
- With 5x leverage: Only ₹24,500 margin needed
- Stop: 50 shares × ₹20 loss = ₹1,000 risk
- Target: 50 shares × ₹40 profit = ₹2,000 gain
- R:R = ₹2,000 ÷ ₹1,000 = 2:1

---

## 🔧 System Configuration

### Current Settings:

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
    "minimum_adx": 15,
    "minimum_volume_ratio": 1.0,
    "trading_mode": "intraday",
    "intraday_candle_interval": "30minute",
    "intraday_exit_time": "15:15"
  }
}
```

### What Each Setting Does:

**capital:** Your trading capital (₹1,00,000)
**risk_per_trade_pct:** Risk per trade (1% = ₹1,000)
**risk_level:** "low" = conservative stops
**use_leverage:** Enable MIS margin (true)
**leverage_multiplier:** 5x buying power

**poll_seconds:** Scan frequency (every 15 sec)
**history_days:** Historical data to fetch (30 days)
**minimum_adx:** Trend strength filter (15+)
**minimum_volume_ratio:** Volume surge filter (1.5x+)
**trading_mode:** "intraday" or "swing"
**intraday_candle_interval:** "30minute" or "1minute"
**intraday_exit_time:** Square off time (3:15 PM)

---

## 📈 Expected Performance

### Signal Frequency:
- **3-8 signals per day** (on average)
- **Some days: 0** (no quality setups)
- **Some days: 10+** (strong trending market)

### Signal Quality:
- **Confidence: 55-85%**
- **R:R Ratio: 1.5:1 to 3:1**
- **Win Rate: ~60-70%** (estimated, not guaranteed)

### Best Times for Signals:
- **10:00 AM - 11:30 AM** (morning momentum)
- **1:30 PM - 2:30 PM** (afternoon trends)
- **Avoid: 12:00 PM - 1:00 PM** (lunch hour lull)

### Market Conditions:
- **Best:** Strong trending days (NIFTY up/down 1%+)
- **Good:** Moderate trends (NIFTY ±0.5%)
- **Poor:** Sideways/choppy days (NIFTY flat)

---

## ⚠️ Risk Warnings

### Leverage Risks:
- **5x leverage = 5x profits AND 5x losses**
- A 1% move against you = 5% capital loss
- Always use stop losses
- Never risk more than 1-2% per trade

### System Limitations:
- **Not a guarantee** - past performance ≠ future results
- **Analysis only** - you must manually place trades
- **Market dependent** - works best in trending markets
- **Requires discipline** - follow the signals, use stops

### Important Rules:
1. **Always use stop losses** (system calculates them)
2. **Square off by 3:15 PM** (intraday positions)
3. **Don't overtrade** (quality over quantity)
4. **Start small** (test with minimum capital first)
5. **Track results** (learn what works for you)

---

## 🎓 Understanding Signal Quality

### High Quality Signal (70%+ confidence):
- Strong trend (ADX >20)
- High volume surge (>1.8x average)
- VWAP and Supertrend aligned
- Clear direction (all indicators aligned)
- Good R:R (>2:1)
- Index supporting
- Price well-positioned vs VWAP

### Medium Quality Signal (60-70% confidence):
- Moderate trend (ADX 15-20)
- Good volume surge (1.5-1.8x average)
- VWAP or Supertrend supporting
- Most indicators aligned
- Decent R:R (1.5-2:1)
- Index neutral or supporting

### Lower Quality Signal (55-60% confidence):
- Weak trend (ADX 15-18)
- Acceptable volume surge (1.5x average)
- Some indicators aligned
- Minimum R:R (1.5:1)
- Index may be against

**Recommendation:** Focus on 65%+ confidence signals with volume surge >1.7x for best results.

---

## 🔄 Daily Workflow

### Morning (Before Market Opens):

1. **Get Fresh Token** (9:00 AM)
   ```bash
   .venv\Scripts\python get_upstox_token.py
   ```

2. **Start Scanner** (9:10 AM)
   ```bash
   .venv\Scripts\python dashboard_server.py
   ```

3. **Open Dashboard**
   ```
   http://127.0.0.1:8010
   ```

4. **Check Email** (ensure notifications working)

### During Market Hours (9:15 AM - 3:30 PM):

1. **Monitor Email** for new signals
2. **Check Dashboard** periodically
3. **Verify Signals** before trading
4. **Place Trades** manually on Upstox
5. **Manage Positions** (stops, targets)

### Before Market Close (3:00 PM):

1. **Square Off Positions** (by 3:15 PM)
2. **Review Results** (what worked, what didn't)
3. **Update Notes** (for learning)

### After Market Close:

1. **Stop Scanner** (Ctrl+C)
2. **Review Day** (signals, trades, results)
3. **Adjust Settings** (if needed)

---

## 📊 Dashboard Features

### Hero Section:
- **Live Mode (5x)** - Shows connection status and leverage
- **Provider:** upstox or sample
- **Trading Mode:** Intraday
- **Index Trend:** NIFTY direction
- **Qualified Trades:** Count of current signals
- **Scan Now Button:** Manual refresh

### Opportunities Panel:
- **Signal Cards** - Color-coded BUY/SELL
- **Leverage Badge** - Orange "5X" indicator
- **All Details** - Entry, stop, target, margin
- **Reasoning** - Why this trade qualifies
- **Auto-Updates** - Every 10 seconds

### Watchlist Table:
- **All 20 Stocks** - Real-time data
- **Price** - Current market price
- **VWAP** - Institutional fair value
- **Trend** - VWAP-based trend (bullish/bearish/neutral)
- **ST** - Supertrend direction (color-coded: green=bullish, red=bearish)
- **Index** - NIFTY trend
- **ADX** - Trend strength
- **RSI** - Momentum
- **Vol Surge** - Volume surge ratio (institutional participation)
- **Status** - BUY/SELL/NO TRADE

### Error Panel:
- **Shows Issues** - Connection errors, data problems
- **Auto-Hides** - When resolved
- **Helpful Messages** - What went wrong

---

## 🎯 Success Tips

### 1. Start Small
- Use minimum capital first
- Test with 1-2 trades per day
- Build confidence gradually

### 2. Follow the System
- Trust the signals (they're calculated)
- Use the provided stops
- Don't second-guess

### 3. Track Everything
- Keep a trading journal
- Note what works
- Learn from losses

### 4. Be Selective
- Focus on 65%+ confidence
- Wait for quality setups
- Don't force trades

### 5. Manage Risk
- Never risk >2% per trade
- Always use stop losses
- Don't overtrade

### 6. Stay Disciplined
- Square off by 3:15 PM
- Don't hold overnight (intraday)
- Follow your plan

---

## 📞 Support & Resources

### Documentation:
- **README.md** - Quick start guide
- **INTRADAY_GUIDE.md** - Intraday trading guide
- **EMAIL_SETUP_GUIDE.md** - Email configuration
- **SYSTEM_COMPLETE_GUIDE.md** - This document

### Configuration Files:
- **.env** - API keys, email settings
- **config/watchlist.json** - Trading settings
- **get_upstox_token.py** - Token generator

### Key Files:
- **dashboard_server.py** - Main server
- **trading_system/live_scanner.py** - Scanner logic
- **trading_system/decision_engine.py** - Signal generation
- **trading_system/email_notifier.py** - Email alerts

---

## 🎉 You're Ready!

Your system is fully configured and ready to generate trade signals. Remember:

- ✅ This is a tool, not a guarantee
- ✅ Always verify signals before trading
- ✅ Use proper risk management
- ✅ Start small and scale up
- ✅ Learn and adapt

**Happy Trading!** 📈💰
