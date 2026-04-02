# Email Notifications Setup Guide

Get instant email alerts when your scanner finds trade opportunities!

---

## 🎯 Quick Setup (Gmail)

### Step 1: Enable 2-Factor Authentication on Gmail

1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification"
3. Follow the setup process

### Step 2: Generate App Password

1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer" (or Other)
3. Click "Generate"
4. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

### Step 3: Configure Your .env File

Edit your `.env` file and add:

```env
# Email Notifications
EMAIL_NOTIFICATIONS_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=abcdefghijklmnop
RECIPIENT_EMAIL=your_email@gmail.com
```

**Replace:**
- `your_email@gmail.com` - Your Gmail address
- `abcdefghijklmnop` - The app password from Step 2 (remove spaces)
- `RECIPIENT_EMAIL` - Can be same or different email

### Step 4: Restart Scanner

```bash
.venv\Scripts\python dashboard_server.py
```

### Step 5: Test It!

When a trade signal appears, you'll get an email like:

```
Subject: 🚨 2 New Trade Signals

BUY - RELIANCE - 75% (5X LEVERAGE)
Entry: 2,450.00
Stop Loss: 2,430.00
Target: 2,490.00
Margin Required: INR 49,000
...
```

---

## 📧 Using Other Email Providers

### Outlook/Hotmail

```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SENDER_EMAIL=your_email@outlook.com
SENDER_PASSWORD=your_password
```

### Yahoo Mail

```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SENDER_EMAIL=your_email@yahoo.com
SENDER_PASSWORD=your_app_password
```

### Custom SMTP Server

```env
SMTP_SERVER=mail.yourdomain.com
SMTP_PORT=587
SENDER_EMAIL=you@yourdomain.com
SENDER_PASSWORD=your_password
```

---

## 🔧 Configuration Options

### Send to Multiple Recipients

Currently supports one recipient. To send to multiple, you can:

1. **Use email forwarding** in your email settings
2. **Modify the code** to support multiple recipients

### Disable Notifications Temporarily

```env
EMAIL_NOTIFICATIONS_ENABLED=false
```

### Change Email Format

Edit `trading_system/email_notifier.py` to customize the email template.

---

## 🛡️ Security Best Practices

### 1. Use App Passwords (Not Your Real Password)
- Never use your actual Gmail password
- Always use app-specific passwords
- Revoke app passwords when not needed

### 2. Keep .env File Private
- Never commit `.env` to Git
- Already in `.gitignore`
- Don't share your `.env` file

### 3. Use Separate Email (Optional)
- Create a dedicated email for trading alerts
- Forward to your main email
- Easier to manage and filter

---

## 🐛 Troubleshooting

### "Authentication Failed"
- Check your app password is correct (no spaces)
- Verify 2FA is enabled on Gmail
- Try regenerating app password

### "Connection Refused"
- Check SMTP server and port
- Verify firewall isn't blocking port 587
- Try port 465 with SSL

### "No Emails Received"
- Check spam/junk folder
- Verify `EMAIL_NOTIFICATIONS_ENABLED=true`
- Check scanner console for error messages
- Verify recipient email is correct

### "Duplicate Emails"
- The system tracks sent signals to avoid duplicates
- Duplicates only if scanner restarts
- This is by design to avoid spam

---

## 📱 Mobile Notifications

### Get Instant Alerts on Phone:

1. **Gmail App** - Enable notifications for your email
2. **Email Filters** - Create filter for "Trade Signal" subject
3. **Priority Inbox** - Mark trading emails as important
4. **Telegram Bot** (Advanced) - Can be added if needed

---

## 🎨 Email Preview

Your emails will look like this:

```
🎯 Intraday Trading Signals

Your scanner has identified the following opportunities:

┌─────────────────────────────────────┐
│ BUY - AXISBANK - 72% [5X LEVERAGE]  │
├─────────────────────────────────────┤
│ Entry: 1,168.40                     │
│ Stop Loss: 1,155.00                 │
│ Target: 1,195.00                    │
│ Position Size: INR 2,92,100         │
│ Margin Required: INR 58,420         │
│ Risk Amount: INR 3,350              │
│ Time Window: same day to 2 sessions │
│                                     │
│ Why this trade:                     │
│ • Price is moving with market trend │
│ • Good participation and volume     │
│ • Clear risk/reward setup           │
└─────────────────────────────────────┘

⚠️ Disclaimer: This is an automated analysis tool.
Remember to square off intraday positions before 3:15 PM IST.
```

---

## ⚙️ Advanced: Customize Notifications

### Only Send High-Confidence Signals

Edit `trading_system/email_notifier.py`:

```python
def send_trade_alert(self, opportunities: List[Dict[str, Any]]) -> None:
    # Filter for high confidence only
    high_conf = [
        opp for opp in opportunities 
        if int(opp.get('confidence', '0%').rstrip('%')) >= 70
    ]
    
    if not high_conf:
        return
    
    # Send email...
```

### Add Sound/Desktop Notification

Install: `pip install plyer`

Then add to `email_notifier.py`:

```python
from plyer import notification

notification.notify(
    title='New Trade Signal',
    message=f"{action} - {asset}",
    timeout=10
)
```

---

## 🎉 You're All Set!

Once configured, you can:
- Leave scanner running in background
- Get instant alerts on your phone/email
- Never miss a quality trade setup
- Focus on other work while scanner watches market

**Pro Tip:** Set up email filters to make trade alerts stand out in your inbox!
