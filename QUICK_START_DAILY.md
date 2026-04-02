# Quick Start - Daily Trading Routine

## 🌅 Morning (9:00 AM) - 30 Seconds

### Option A: Automatic (Recommended)
```bash
# Just run this one command:
.venv\Scripts\python start_trading_day.py
```

**What happens:**
1. Browser opens for Upstox authorization
2. Click "Authorize" button
3. Scanner starts automatically
4. Dashboard opens in browser
5. Done! ✅

### Option B: Manual (Traditional)
```bash
# Step 1: Generate token
.venv\Scripts\python get_upstox_token.py

# Step 2: Start scanner
.venv\Scripts\python dashboard_server.py
```

## 📧 During Market Hours (9:15 AM - 3:30 PM)

**You don't need to do anything!**

The system will:
- ✅ Scan every 15 seconds automatically
- ✅ Send email when signals appear
- ✅ Block bad trading windows
- ✅ Update dashboard in real-time

**You just:**
- 📱 Check email for trade alerts
- 💼 Execute trades on Upstox
- 😎 Go about your day

## 🌆 Evening (3:30 PM) - 10 Seconds

```bash
# Press Ctrl+C in the terminal
# Or just close the terminal window
```

**That's it!**

## 📊 Expected Signal Frequency

Based on current filters:

| Market Condition | Expected Signals |
|-----------------|------------------|
| Strong trending day | 5-10 signals |
| Normal day | 2-5 signals |
| Choppy/sideways day | 0-2 signals |
| Very volatile day | 0-1 signals (filters block) |

**Average: 3-5 signals per day**

Most of the day = "NO TRADE" (this is good, staying selective!)

## 💡 Pro Tips

1. **Email is enough** - You don't need to watch the dashboard
2. **Focus on 65%+ confidence** - Better win rate
3. **Best times: 10-11:30 AM, 1:30-2:30 PM** - Most signals appear here
4. **Don't force trades** - Some days have 0 signals (by design)
5. **Square off by 3:15 PM** - Don't carry intraday positions overnight

## 🎯 Typical Day

```
9:00 AM  ⏰ Run start_trading_day.py (30 seconds)
9:05 AM  ✅ Scanner running, minimize window
         📱 Go about your day

10:23 AM 📧 "2 New Trade Signals" 
         💼 Execute trades on Upstox (2 minutes)

11:47 AM 📧 "1 New Trade Signal"
         💼 Execute trade (1 minute)

2:15 PM  📧 "3 New Trade Signals"
         💼 Execute best 2 trades (2 minutes)

3:15 PM  💼 Square off all positions
3:30 PM  🛑 Stop scanner (Ctrl+C)

Total active time: ~6 minutes
Total monitoring time: 0 minutes (email does it)
```

## ⚠️ Important Reminders

- ✅ Token expires daily (must regenerate each morning)
- ✅ Square off intraday positions by 3:15 PM
- ✅ Email notifications = your safety net
- ✅ Dashboard is optional (nice to have, not required)
- ✅ System is selective (0 signals on bad days is normal)

## 🚀 You're All Set!

Your system is now:
- ✅ Fully automated scanning
- ✅ Email notifications enabled
- ✅ Professional filters active
- ✅ Leverage support (5x)
- ✅ Risk management built-in

Just run `start_trading_day.py` each morning and check your email! 📧💰
