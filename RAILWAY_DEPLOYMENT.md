# Deploy to Railway.app (FREE Alternative)

## Why Railway?

✅ **FREE** ($5 credit/month, enough for trading hours)
✅ **No sleep** (stays awake unlike Render free tier)
✅ **Easy deployment** (one-click from GitHub)
✅ **Environment variables** (update token daily)
✅ **Better for long-running processes**

## Step-by-Step Deployment

### 1. Create Railway Account

1. Go to https://railway.app
2. Sign up with GitHub (free)
3. Get $5 free credit/month (no credit card needed)

### 2. Deploy Your App

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository
4. Railway auto-detects Python and deploys

### 3. Add Environment Variables

1. Click on your service
2. Go to "Variables" tab
3. Add all from your `.env`:
   ```
   UPSTOX_API_KEY=your_key
   UPSTOX_API_SECRET=your_secret
   UPSTOX_ACCESS_TOKEN=your_token
   UPSTOX_REDIRECT_URI=http://localhost:8000
   EMAIL_ENABLED=true
   EMAIL_FROM=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   EMAIL_TO=your-phone-email@gmail.com
   EMAIL_SMTP_SERVER=smtp.gmail.com
   EMAIL_SMTP_PORT=587
   ```

4. Click "Deploy" to restart with new variables

### 4. Daily Token Update (1 Minute)

**Every morning at 9:00 AM:**

1. On your PC:
   ```bash
   .venv\Scripts\python get_upstox_token.py
   ```

2. Copy token from `.env`

3. Railway dashboard:
   - Variables tab
   - Update `UPSTOX_ACCESS_TOKEN`
   - Auto-redeploys (30 seconds)

4. Done! Email notifications work all day

### 5. Monitor

**View Logs:**
- Click "Deployments" tab
- See real-time logs

**Check Dashboard:**
- Railway gives you a public URL
- Visit to see trading signals

**Email Notifications:**
- Work automatically from cloud

## Cost Analysis

Railway free tier:
- **$5 credit/month**
- **~$0.01/hour** for small apps
- **Trading hours:** 6.5 hrs/day × 22 days = 143 hrs/month
- **Cost:** ~$1.43/month
- **Remaining credit:** $3.57 for other projects

**Verdict: Completely free for trading scanner!** ✅

## Comparison: Render vs Railway

| Feature | Render Free | Railway Free |
|---------|-------------|--------------|
| Cost | Free (750 hrs) | $5 credit/month |
| Sleep | Yes (15 min) | No |
| Restart | Manual wake | Always on |
| Best for | Hobby projects | Production apps |
| Trading use | ⚠️ Needs ping | ✅ Perfect |

## Recommendation

**For Trading Scanner:**
1. **Railway** - Better (no sleep, always on)
2. **Render** - Good (needs ping to stay awake)

Both are free and work well!

## Next Steps

1. Sign up at railway.app
2. Deploy from GitHub
3. Add environment variables
4. Update token daily (1 min)
5. Get email notifications all day

No laptop needed! 🚀
