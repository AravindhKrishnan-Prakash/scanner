"""Test email notification system"""
import os
from pathlib import Path
from trading_system.config import load_env_file
from trading_system.email_notifier import EmailNotifier

# Load environment variables
ROOT = Path(__file__).resolve().parent
load_env_file(ROOT / ".env")

# Create test opportunity
test_opportunity = {
    "action": "BUY",
    "asset": "RELIANCE",
    "confidence": "75%",
    "entry": "2,450.00",
    "stop_loss": "2,430.00",
    "target": "2,490.00",
    "position_size": "INR 2,45,000",
    "risk_amount": "INR 2,000",
    "time_window": "same day to 2 sessions",
    "leverage": "5X",
    "margin_required": "INR 49,000",
    "exposure": "INR 2,45,000",
    "reason": [
        "Price is moving in the same direction as the broader market.",
        "The setup has room to move higher before the next major barrier.",
        "Participation is healthy, which supports follow-through.",
        "Risk is controlled with a clear exit level if the idea fails."
    ]
}

test_opportunity2 = {
    "action": "SELL",
    "asset": "AXISBANK",
    "confidence": "72%",
    "entry": "1,168.40",
    "stop_loss": "1,180.00",
    "target": "1,145.00",
    "position_size": "INR 2,92,100",
    "risk_amount": "INR 2,900",
    "time_window": "same day to 2 sessions",
    "leverage": "5X",
    "margin_required": "INR 58,420",
    "exposure": "INR 2,92,100",
    "reason": [
        "Price is weakening in line with the broader market backdrop.",
        "The setup has room to move lower before the next major barrier.",
        "Participation is acceptable for a controlled trade.",
        "Risk is controlled with a clear exit level if the idea fails."
    ]
}

print("=" * 60)
print("Testing Email Notification System")
print("=" * 60)

# Check configuration
enabled = os.environ.get("EMAIL_NOTIFICATIONS_ENABLED", "false").lower() == "true"
sender = os.environ.get("SENDER_EMAIL", "")
recipient = os.environ.get("RECIPIENT_EMAIL", "")

print(f"\nConfiguration:")
print(f"  Enabled: {enabled}")
print(f"  Sender: {sender}")
print(f"  Recipient: {recipient}")
print(f"  SMTP Server: {os.environ.get('SMTP_SERVER', 'smtp.gmail.com')}")
print(f"  SMTP Port: {os.environ.get('SMTP_PORT', '587')}")

if not enabled:
    print("\n❌ Email notifications are DISABLED")
    print("   Set EMAIL_NOTIFICATIONS_ENABLED=true in .env file")
    exit(1)

if not sender or not recipient:
    print("\n❌ Email addresses not configured")
    print("   Set SENDER_EMAIL and RECIPIENT_EMAIL in .env file")
    exit(1)

print("\n" + "=" * 60)
print("Sending test email with 2 sample trade signals...")
print("=" * 60)

try:
    notifier = EmailNotifier()
    notifier.send_trade_alert([test_opportunity, test_opportunity2])
    
    print("\n✅ SUCCESS! Test email sent!")
    print(f"\n📧 Check your inbox: {recipient}")
    print("\nIf you don't see it:")
    print("  1. Check spam/junk folder")
    print("  2. Wait 1-2 minutes for delivery")
    print("  3. Verify email settings in .env file")
    
except Exception as e:
    print(f"\n❌ FAILED to send email!")
    print(f"\nError: {e}")
    print("\nCommon issues:")
    print("  1. Wrong app password (check for typos)")
    print("  2. 2FA not enabled on Gmail")
    print("  3. App password not generated")
    print("  4. Firewall blocking port 587")
    print("\nSee EMAIL_SETUP_GUIDE.md for help")

print("\n" + "=" * 60)
