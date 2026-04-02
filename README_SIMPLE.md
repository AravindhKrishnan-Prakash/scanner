# India Live Trading Scanner - Simple Guide

## What This System Does

🔍 **Scans 20 stocks every 15 seconds**
📊 **Analyzes 11 technical indicators**
🎯 **Finds 3-5 quality trade signals per day**
📧 **Sends email alerts instantly**
💰 **Calculates position size with 5x leverage**

## Daily Workflow (30 Seconds)

### Morning (9:00 AM)
```bash
.venv\Scripts\python start_trading_day.py
```
Click "Authorize" when browser opens. Done!

### During Market Hours
📧 Check email for trade alerts
💼 Execute trades on Upstox
😎 That's it!

### Evening (3:30 PM)
Press Ctrl+C to stop scanner

## Email Notifications = Your Safety Net

You don't need to watch the dashboard all day!

✅ Email alerts when signals appear
✅ Works on your phone
✅ Instant notifications
✅ All trade details included

**Most of the day = NO TRADE (by design)**
**You only get emails when quality setups appear**

## Hosting Options

### Option 1: Local PC (Recommended)
- Run on your Windows PC
- Auto-start at 9:05 AM (optional)
- Free, simple, reliable
- Just click "Authorize" each morning (10 seconds)

### Option 2: Cloud Server
- Run on AWS/DigitalOcean
- Access from anywhere
- Costs ₹400-800/month
- Still need to update token daily

**Recommendation: Start with Option 1**

## Why Token Can't Be Fully Automated

Upstox requires manual authorization each day for security:
- Industry standard practice
- Protects your trading account
- Takes only 10 seconds
- Cannot be bypassed (security feature)

## Expected Results

| Day Type | Signals | Your Time |
|----------|---------|-----------|
| Strong trending | 5-10 | 5-10 min |
| Normal | 2-5 | 2-5 min |
| Choppy | 0-2 | 0-2 min |

**Average: 3-5 signals per day, 5 minutes of work**

## Files You Need to Know

- **start_trading_day.py** - One-click daily startup
- **QUICK_START_DAILY.md** - Daily routine guide
- **HOSTING_GUIDE.md** - Hosting options explained
- **.env** - Your API keys and email settings
- **config/watchlist.json** - Trading settings

## Support Documents

- **SYSTEM_COMPLETE_GUIDE.md** - Full technical details
- **FILTER_ADJUSTMENTS.md** - Recent changes explained
- **EMAIL_SETUP_GUIDE.md** - Email configuration
- **INTRADAY_GUIDE.md** - Intraday trading guide

## Quick Answers

**Q: Do I need to watch the dashboard all day?**
A: No! Email notifications are enough.

**Q: Can I host this on a server?**
A: Yes, but you still need to update token daily (10 sec task).

**Q: Why am I getting 0 signals?**
A: System is selective. Some days have no quality setups (normal).

**Q: Can I automate token generation?**
A: No, Upstox requires manual authorization (security policy).

**Q: Is email notification reliable?**
A: Yes! Instant delivery to your phone. Test with test_email.py.

## You're Ready! 🚀

1. Run `start_trading_day.py` each morning
2. Check email for trade alerts
3. Execute trades on Upstox
4. Square off by 3:15 PM

That's it! The system does the heavy lifting. 📈💰
