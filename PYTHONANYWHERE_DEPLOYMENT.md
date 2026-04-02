# Deploy to PythonAnywhere (FREE)

## Why PythonAnywhere?

✅ **Completely FREE** (beginner account)
✅ **Python-focused** (perfect for this project)
✅ **Always-on** (no sleep)
✅ **Easy setup** (web-based console)
✅ **Scheduled tasks** (can auto-update token)

## Step-by-Step Deployment

### 1. Create Account

1. Go to https://www.pythonanywhere.com
2. Sign up for FREE "Beginner" account
3. Verify email

### 2. Upload Your Code

**Option A: Git Clone (Recommended)**
1. Open "Bash console" from dashboard
2. Clone your repo:
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo
   ```

**Option B: Upload Files**
1. Go to "Files" tab
2. Upload your project folder
3. Extract if zipped

### 3. Install Dependencies

In Bash console:
```bash
cd your-repo
pip3 install --user -r requirements.txt
```

### 4. Set Up Environment Variables

Create `.env` file:
```bash
nano .env
```

Paste your variables:
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

Save: Ctrl+X, Y, Enter

### 5. Create Web App

1. Go to "Web" tab
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select Python 3.10
5. Set working directory: `/home/yourusername/your-repo`
6. Set WSGI file to point to `dashboard_server.py`

### 6. Configure WSGI

Edit WSGI configuration file:
```python
import sys
import os

# Add your project directory
project_home = '/home/yourusername/your-repo'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

# Import your app
from dashboard_server import app as application
```

### 7. Start the App

1. Click "Reload" button on Web tab
2. Visit your URL: `yourusername.pythonanywhere.com`
3. Scanner is now running!

### 8. Daily Token Update (2 Minutes)

**Every morning at 9:00 AM:**

1. On your PC:
   ```bash
   .venv\Scripts\python get_upstox_token.py
   ```

2. Copy token

3. PythonAnywhere:
   - Open Bash console
   - Edit `.env`:
     ```bash
     cd your-repo
     nano .env
     ```
   - Update `UPSTOX_ACCESS_TOKEN`
   - Save and exit
   - Reload web app

4. Done!

## Pros & Cons

### Pros ✅
- Completely free forever
- No credit card needed
- Python-focused (easy setup)
- Always-on (no sleep)
- Web-based console
- Can schedule tasks

### Cons ⚠️
- Free tier has CPU limits (should be fine for scanner)
- Manual token update (2 min/day)
- Web interface only (no CLI)

## Free Tier Limits

- **CPU seconds/day:** 100 seconds
- **Disk space:** 512 MB
- **Always-on:** 1 web app
- **Enough for trading?** ✅ Yes!

Your scanner uses minimal CPU (just API calls every 15 sec).

## Comparison: All Free Options

| Platform | Setup Time | Always-On | Token Update | Best For |
|----------|-----------|-----------|--------------|----------|
| Render | 10 min | ⚠️ Sleeps | 1 min (web UI) | Easy deployment |
| Railway | 5 min | ✅ Yes | 1 min (web UI) | Best overall |
| PythonAnywhere | 15 min | ✅ Yes | 2 min (console) | Python devs |
| Local PC | 2 min | ✅ Yes | 10 sec (auto) | Simplest |

## My Recommendation

**Best FREE cloud option: Railway** ⭐
- Easiest setup
- No sleep issues
- Clean web UI
- $5 credit covers trading hours

**Best overall: Local PC with auto-start** ⭐⭐⭐
- Completely free
- Fastest token update (10 sec)
- No cloud limits
- Full control

## Next Steps

Choose your platform:

1. **Railway** (recommended cloud) → See RAILWAY_DEPLOYMENT.md
2. **Render** (good cloud) → See RENDER_DEPLOYMENT.md
3. **PythonAnywhere** (Python-focused) → This guide
4. **Local PC** (simplest) → Use start_trading_day.py

All options work! Pick what suits you best. 🚀
