# Deploy to Render.com (FREE) ⭐ RECOMMENDED

## Why Render?

✅ **Completely FREE** (750 hours/month free tier)
✅ **Always-on** (runs 24/7)
✅ **Easy deployment** (connect GitHub)
✅ **Environment variables** (update token daily via dashboard)
✅ **Logs viewer** (see what's happening)
✅ **Auto-restart** (if crashes)

## Step-by-Step Deployment

### 1. Prepare Your Code

Create a `render.yaml` file in your project root:

```yaml
services:
  - type: web
    name: trading-scanner
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python dashboard_server.py
    envVars:
      - key: UPSTOX_API_KEY
        sync: false
      - key: UPSTOX_API_SECRET
        sync: false
      - key: UPSTOX_ACCESS_TOKEN
        sync: false
      - key: UPSTOX_REDIRECT_URI
        value: http://localhost:8000
      - key: EMAIL_ENABLED
        value: true
      - key: EMAIL_FROM
        sync: false
      - key: EMAIL_PASSWORD
        sync: false
      - key: EMAIL_TO
        sync: false
      - key: EMAIL_SMTP_SERVER
        value: smtp.gmail.com
      - key: EMAIL_SMTP_PORT
        value: 587
```

### 2. Create Render Account

1. Go to https://render.com
2. Sign up with GitHub (free)
3. Verify your email

### 3. Deploy Your App

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name:** trading-scanner
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python dashboard_server.py`
   - **Plan:** Free

4. Add Environment Variables:
   - Click "Environment" tab
   - Add all variables from your `.env` file
   - Click "Save Changes"

### 4. Deploy!

Click "Create Web Service" - Render will:
- Clone your code
- Install dependencies
- Start the scanner
- Give you a URL (e.g., https://trading-scanner.onrender.com)

### 5. Daily Token Update (2 Minutes)

**Every morning at 9:00 AM:**

1. On your PC, run:
   ```bash
   .venv\Scripts\python get_upstox_token.py
   ```

2. Copy the access token from `.env` file

3. Go to Render dashboard:
   - Open your service
   - Click "Environment" tab
   - Find `UPSTOX_ACCESS_TOKEN`
   - Paste new token
   - Click "Save Changes"

4. Render auto-restarts (takes 30 seconds)

5. Done! Scanner runs all day, you get email notifications

### 6. Monitor Your Scanner

**View Logs:**
- Go to Render dashboard
- Click "Logs" tab
- See real-time scanner activity

**Check Dashboard:**
- Visit your Render URL
- See live trading signals

**Email Notifications:**
- Work automatically
- No need to check dashboard

## Pros & Cons

### Pros ✅
- Completely free (750 hours/month)
- No credit card required
- Easy deployment
- Auto-restart on crashes
- Environment variable updates
- Logs viewer
- No laptop needed

### Cons ⚠️
- Free tier sleeps after 15 min inactivity (but wakes up automatically)
- Need to update token daily (2 min task)
- Limited to 750 hours/month (enough for trading hours)

## Cost Breakdown

| Service | Free Tier | Enough for Trading? |
|---------|-----------|---------------------|
| Render | 750 hrs/month | ✅ Yes (6.5 hrs/day × 22 days = 143 hrs) |
| Vercel | ❌ No long-running | ❌ No |
| Heroku | ❌ No free tier anymore | ❌ No |
| Railway | 500 hrs/month | ✅ Yes |

## Alternative: Keep It Awake

Render free tier sleeps after 15 min inactivity. To prevent this:

**Option A: Cron Job (Recommended)**
Use a free service like cron-job.org to ping your app every 10 minutes:
- URL: https://your-app.onrender.com
- Interval: Every 10 minutes
- Time: 9:00 AM - 3:30 PM IST

**Option B: Self-Ping**
Add this to your scanner (already built-in):
```python
# Scanner pings itself every 10 minutes
# Keeps Render awake during market hours
```

## Security Notes

1. **Never commit .env to GitHub** - Use Render's environment variables
2. **Use app passwords** for email (not main password)
3. **Rotate tokens regularly** - Upstox forces daily rotation anyway
4. **Enable 2FA on Render** - Extra security

## Troubleshooting

**Scanner not starting?**
- Check logs in Render dashboard
- Verify all environment variables are set
- Check if token is valid

**Not receiving emails?**
- Test with `test_email.py` locally first
- Check email password is app password (not main password)
- Verify EMAIL_ENABLED=true

**Scanner sleeping?**
- Set up cron job to ping every 10 minutes
- Or upgrade to paid plan ($7/month for always-on)

## Next Steps

1. Create `render.yaml` file (see above)
2. Push to GitHub
3. Deploy to Render
4. Add environment variables
5. Test email notifications
6. Update token daily at 9:00 AM

You're done! Scanner runs on cloud, you get email notifications, no laptop needed! 🚀
