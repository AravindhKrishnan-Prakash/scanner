# Hosting Guide - Run Scanner 24/7

## The Token Challenge

Upstox requires **manual authorization** each day for security:
1. You click a link
2. Login to Upstox
3. Authorize the app
4. Get access token

This **cannot be fully automated** (Upstox security policy).

## Solution Options

### Option 1: Local PC with Auto-Start (RECOMMENDED)

**Best for:** Home traders with a PC that stays on

**Setup:**
1. Run `setup_auto_start.bat` (as Administrator)
2. Each morning at 9:05 AM:
   - Browser opens automatically
   - Click "Authorize" (takes 10 seconds)
   - Scanner starts automatically
3. Email notifications work all day
4. PC can be minimized/locked (scanner keeps running)

**Pros:**
- ✅ Free (no hosting costs)
- ✅ Email notifications work
- ✅ Only 10 seconds of work each morning
- ✅ Full control

**Cons:**
- ❌ PC must stay on during market hours
- ❌ Need to authorize token daily (10 sec task)

### Option 2: Cloud Server with Manual Token Update

**Best for:** Advanced users, multiple users

**Setup:**
1. Deploy to AWS/DigitalOcean/Heroku
2. Each morning (9:00 AM):
   - Run token generator on your local PC
   - Copy token to cloud server (via SSH or web interface)
   - Scanner runs on cloud all day
3. Email notifications work from anywhere

**Pros:**
- ✅ Access from anywhere
- ✅ No need to keep PC on
- ✅ Can share with team

**Cons:**
- ❌ Costs $5-10/month
- ❌ Still need to update token daily
- ❌ More complex setup

### Option 3: Mobile Token Update (Future Enhancement)

**Concept:** Create a mobile app or web interface where you can:
1. Login to Upstox from phone
2. Generate token with one tap
3. Scanner on cloud picks it up automatically

**Status:** Not implemented yet (would require additional development)

## Recommended Workflow

### For Most Users (Option 1):

**One-Time Setup:**
```bash
# Run as Administrator
setup_auto_start.bat
```

**Daily Routine (10 seconds):**
1. At 9:05 AM, browser opens automatically
2. Click "Authorize" button
3. Done! Scanner runs all day
4. Check email for trade alerts
5. Execute trades on Upstox app/website

**End of Day:**
- Scanner stops automatically at 3:30 PM (or you can Ctrl+C)
- Or just let it run (it won't do anything after market close)

### For Cloud Hosting (Option 2):

**One-Time Setup:**
1. Deploy to cloud server (AWS EC2, DigitalOcean Droplet, etc.)
2. Install Python and dependencies
3. Configure email settings
4. Set up SSH access

**Daily Routine:**

**Method A: SSH Token Update**
```bash
# On your local PC (9:00 AM)
.venv\Scripts\python get_upstox_token.py

# Copy token from .env file
# SSH to cloud server
ssh user@your-server.com

# Update .env on server
nano .env
# Paste new token
# Save and exit

# Restart scanner
pm2 restart trading-scanner
```

**Method B: Web Interface (requires additional development)**
- Create a simple web page
- Upload token through browser
- Scanner picks it up automatically

## Email Notification Setup

**Critical for hosted systems!**

Make sure your `.env` has:
```
EMAIL_ENABLED=true
EMAIL_FROM=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_TO=your-phone-email@gmail.com
```

Then you get notifications on your phone even if:
- Dashboard is closed
- PC is locked
- You're away from computer

## Cost Comparison

| Option | Setup Time | Daily Time | Monthly Cost | Convenience |
|--------|-----------|------------|--------------|-------------|
| Local PC Auto-Start | 5 min | 10 sec | ₹0 | ⭐⭐⭐⭐⭐ |
| Cloud + Manual Token | 2 hours | 2 min | ₹400-800 | ⭐⭐⭐ |
| Fully Manual | 0 min | 5 min | ₹0 | ⭐⭐ |

## My Recommendation

**Start with Local PC Auto-Start:**
1. Run `setup_auto_start.bat`
2. Each morning: Click "Authorize" (10 seconds)
3. Check email for signals
4. Execute trades

**Later, if needed:**
- Move to cloud hosting
- Share with team members
- Build mobile token update app

## Security Notes

1. **Never share your access token** - It gives full trading access
2. **Use app passwords** for email (not your main password)
3. **Keep .env file private** - Don't commit to GitHub
4. **Tokens expire daily** - This is a security feature, not a bug
5. **Use 2FA on Upstox** - Extra security for your trading account

## Questions?

**Q: Can I fully automate token generation?**
A: No, Upstox requires manual authorization for security. This is industry standard.

**Q: What if I forget to generate token?**
A: Scanner will show errors, no signals will be generated. Just generate token and restart.

**Q: Can I run on Raspberry Pi?**
A: Yes! Same as local PC option. Very power-efficient.

**Q: Can I run on Android phone?**
A: Possible with Termux, but not recommended. Use cloud hosting instead.

**Q: What about weekends?**
A: Market is closed, no need to run scanner. Auto-start only runs Mon-Fri.

## Next Steps

1. Choose your hosting option
2. Set up auto-start (if using Option 1)
3. Test email notifications
4. Run for a few days to verify
5. Adjust filters if needed based on signal quality
