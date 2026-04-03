"""Email notification system for trade signals"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any


class EmailNotifier:
    def __init__(self):
        self.enabled = os.environ.get("EMAIL_NOTIFICATIONS_ENABLED", "false").lower() == "true"
        self.smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        self.sender_email = os.environ.get("SENDER_EMAIL", "")
        self.sender_password = os.environ.get("SENDER_PASSWORD", "")
        self.recipient_email = os.environ.get("RECIPIENT_EMAIL", "")
        
        # Track sent notifications to avoid duplicates
        self._sent_signals = set()
    
    def send_trade_alert(self, opportunities: List[Dict[str, Any]]) -> None:
        """Send email alert for new trade opportunities"""
        print(f"📧 Email notification triggered with {len(opportunities)} opportunities")
        print(f"   EMAIL_NOTIFICATIONS_ENABLED: {self.enabled}")
        print(f"   Sender email configured: {bool(self.sender_email)}")
        print(f"   Recipient email configured: {bool(self.recipient_email)}")
        
        if not self.enabled:
            print("⚠ Email notifications are DISABLED")
            return
        
        if not self.sender_email or not self.recipient_email:
            print("⚠ Email notifications enabled but email addresses not configured")
            print(f"   SENDER_EMAIL: {self.sender_email or 'NOT SET'}")
            print(f"   RECIPIENT_EMAIL: {self.recipient_email or 'NOT SET'}")
            return
        
        # Filter out already-sent signals
        new_opportunities = []
        for opp in opportunities:
            signal_id = f"{opp.get('asset')}_{opp.get('action')}_{opp.get('entry')}"
            if signal_id not in self._sent_signals:
                new_opportunities.append(opp)
                self._sent_signals.add(signal_id)
        
        if not new_opportunities:
            print(f"⚠ All {len(opportunities)} signals already sent before (duplicates filtered)")
            return
        
        print(f"✓ Sending email for {len(new_opportunities)} NEW signals...")
        
        try:
            subject = f"🚨 {len(new_opportunities)} New Trade Signal{'s' if len(new_opportunities) > 1 else ''}"
            body = self._format_email_body(new_opportunities)
            
            self._send_email(subject, body)
            print(f"✓ Email sent successfully: {len(new_opportunities)} signal(s)")
        except Exception as e:
            print(f"✗ Failed to send email: {e}")
            import traceback
            traceback.print_exc()
    
    def _format_email_body(self, opportunities: List[Dict[str, Any]]) -> str:
        """Format opportunities into email body"""
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                .signal { 
                    border: 2px solid #ddd; 
                    border-radius: 10px; 
                    padding: 15px; 
                    margin: 15px 0;
                    background: #f9f9f9;
                }
                .buy { border-color: #28a745; background: #d4edda; }
                .sell { border-color: #dc3545; background: #f8d7da; }
                .header { font-size: 18px; font-weight: bold; margin-bottom: 10px; }
                .detail { margin: 5px 0; }
                .label { font-weight: bold; color: #555; }
                .value { color: #000; }
                .leverage { 
                    display: inline-block;
                    background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
                    color: white;
                    padding: 3px 8px;
                    border-radius: 5px;
                    font-size: 12px;
                    font-weight: bold;
                }
                .reasons { 
                    margin-top: 10px; 
                    padding-left: 20px;
                    color: #666;
                }
            </style>
        </head>
        <body>
            <h2>🎯 Intraday Trading Signals</h2>
            <p>Your scanner has identified the following opportunities:</p>
        """
        
        for opp in opportunities:
            action = opp.get('action', 'NO TRADE')
            asset = opp.get('asset', 'Unknown')
            confidence = opp.get('confidence', '0%')
            entry = opp.get('entry', '0.00')
            stop = opp.get('stop_loss', '0.00')
            target = opp.get('target', '0.00')
            position = opp.get('position_size', 'INR 0.00')
            risk = opp.get('risk_amount', 'INR 0.00')
            time_window = opp.get('time_window', 'Unknown')
            leverage = opp.get('leverage', '')
            margin = opp.get('margin_required', '')
            exposure = opp.get('exposure', '')
            reasons = opp.get('reason', [])
            
            signal_class = 'buy' if action == 'BUY' else 'sell'
            leverage_badge = f'<span class="leverage">{leverage}</span>' if leverage else ''
            
            html += f"""
            <div class="signal {signal_class}">
                <div class="header">
                    {action} - {asset} - {confidence} {leverage_badge}
                </div>
                <div class="detail">
                    <span class="label">Entry:</span> 
                    <span class="value">{entry}</span>
                </div>
                <div class="detail">
                    <span class="label">Stop Loss:</span> 
                    <span class="value">{stop}</span>
                </div>
                <div class="detail">
                    <span class="label">Target:</span> 
                    <span class="value">{target}</span>
                </div>
                <div class="detail">
                    <span class="label">Position Size:</span> 
                    <span class="value">{position}</span>
                </div>
            """
            
            if margin:
                html += f"""
                <div class="detail">
                    <span class="label">Margin Required:</span> 
                    <span class="value">{margin}</span>
                </div>
                """
            
            if exposure:
                html += f"""
                <div class="detail">
                    <span class="label">Total Exposure:</span> 
                    <span class="value">{exposure}</span>
                </div>
                """
            
            html += f"""
                <div class="detail">
                    <span class="label">Risk Amount:</span> 
                    <span class="value">{risk}</span>
                </div>
                <div class="detail">
                    <span class="label">Time Window:</span> 
                    <span class="value">{time_window}</span>
                </div>
            """
            
            if reasons:
                html += '<div class="reasons"><strong>Why this trade:</strong><ul>'
                for reason in reasons[:4]:
                    html += f'<li>{reason}</li>'
                html += '</ul></div>'
            
            html += '</div>'
        
        html += """
            <hr>
            <p style="color: #666; font-size: 12px;">
                ⚠️ <strong>Disclaimer:</strong> This is an automated analysis tool. 
                Always verify signals and manage your own risk. Past performance does not guarantee future results.
            </p>
            <p style="color: #666; font-size: 12px;">
                Remember to square off intraday positions before 3:15 PM IST.
            </p>
        </body>
        </html>
        """
        
        return html
    
    def _send_email(self, subject: str, body: str) -> None:
        """Send email via SMTP"""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = self.sender_email
        msg['To'] = self.recipient_email
        
        # Attach HTML body
        html_part = MIMEText(body, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
    
    def clear_sent_signals(self) -> None:
        """Clear the cache of sent signals (call this daily)"""
        self._sent_signals.clear()
