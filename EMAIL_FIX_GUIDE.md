# EMAIL NOTIFICATION FIX GUIDE

## Problem
Newsletter subscriptions succeed but no email is sent. Order emails also not being sent.

## Root Cause
**PythonAnywhere blocks Gmail SMTP on port 587 for free accounts.**

## Solutions (Choose One)

### Solution 1: Upgrade PythonAnywhere (Recommended)
**Cost:** $5/month for Hacker plan
**Benefit:** Unrestricted SMTP access

1. Upgrade at: https://www.pythonanywhere.com/pricing/
2. No code changes needed
3. Emails will work immediately

---

### Solution 2: Use SendGrid (FREE Alternative)
**Cost:** FREE (100 emails/day)
**Setup Time:** 5 minutes

#### Step 1: Get SendGrid API Key
1. Sign up: https://signup.sendgrid.com/
2. Go to Settings → API Keys
3. Create API key with "Mail Send" permission
4. Copy the API key

#### Step 2: Update .env file on PythonAnywhere
```bash
# Add to .env file
SENDGRID_API_KEY=your_api_key_here
SENDGRID_FROM_EMAIL=michealbyers750@gmail.com
```

#### Step 3: Install SendGrid
```bash
cd ~/wegatsauceefashionhub
source ~/.virtualenvs/myenv/bin/activate
pip install sendgrid
```

#### Step 4: Update email_notifications.py
Replace the entire file with:

```python
from decouple import config
import os

# Check if SendGrid is available
USE_SENDGRID = config('SENDGRID_API_KEY', default=None) is not None

if USE_SENDGRID:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    
    def send_email(to_email, subject, html_content):
        try:
            message = Mail(
                from_email=config('SENDGRID_FROM_EMAIL'),
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            sg = SendGridAPIClient(config('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(f"[EMAIL] Sent via SendGrid to {to_email} - Status: {response.status_code}")
            return True
        except Exception as e:
            print(f"[EMAIL ERROR] SendGrid failed: {e}")
            return False
else:
    # Fallback to Gmail SMTP
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    def send_email(to_email, subject, html_content):
        try:
            from_email = config('EMAIL_USER')
            password = config('EMAIL_PASSWORD')
            host = config('EMAIL_HOST')
            port = int(config('EMAIL_PORT'))
            
            msg = MIMEMultipart('alternative')
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            server = smtplib.SMTP(host, port, timeout=10)
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
            server.quit()
            print(f"[EMAIL] Sent via Gmail to {to_email}")
            return True
        except Exception as e:
            print(f"[EMAIL ERROR] Gmail SMTP failed: {e}")
            return False

# Keep all other functions the same (send_order_confirmation, etc.)
def send_order_confirmation(user, order):
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0;">Order Confirmed!</h1>
        </div>
        <div style="padding: 30px; background: #f9f9f9;">
            <p>Hi {user.name},</p>
            <p>Thank you for your order! We've received your order and will process it soon.</p>
            
            <div style="background: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h2 style="color: #667eea;">Order #{order.id}</h2>
                <p><strong>Total:</strong> KSh {order.total:,.0f}</p>
                <p><strong>Status:</strong> {order.status.title()}</p>
                <p><strong>Expected Delivery:</strong> {order.expected_delivery.strftime('%B %d, %Y')}</p>
            </div>
            
            <p>We'll send you another email when your order ships.</p>
            <p style="margin-top: 30px;">Best regards,<br><strong>Wegatsaucee Fashion Hub</strong></p>
        </div>
    </body>
    </html>
    """
    return send_email(user.email, f"Order #{order.id} Confirmed - Wegatsaucee", html)

def send_shipping_notification(user, order):
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0;">📦 Your Order is On The Way!</h1>
        </div>
        <div style="padding: 30px; background: #f9f9f9;">
            <p>Hi {user.name},</p>
            <p>Great news! Your order has been shipped and is on its way to you.</p>
            
            <div style="background: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h2 style="color: #f5576c;">Order #{order.id}</h2>
                <p><strong>Expected Delivery:</strong> {order.expected_delivery.strftime('%B %d, %Y')}</p>
            </div>
            
            <p>Track your order: <a href="https://emonigatsaucee.pythonanywhere.com/track/{order.id}">Click here</a></p>
            <p style="margin-top: 30px;">Best regards,<br><strong>Wegatsaucee Fashion Hub</strong></p>
        </div>
    </body>
    </html>
    """
    return send_email(user.email, f"Order #{order.id} Shipped! - Wegatsaucee", html)

def send_tracking_update(user, order, tracking):
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0;">📍 Order Update</h1>
        </div>
        <div style="padding: 30px; background: #f9f9f9;">
            <p>Hi {user.name},</p>
            <p>Your order has a new update!</p>
            
            <div style="background: white; padding: 20px; border-radius: 10px; margin: 20px 0;">
                <h2 style="color: #4facfe;">Order #{order.id}</h2>
                <p><strong>Location:</strong> {tracking.location}</p>
                <p><strong>Transport:</strong> {tracking.transport_company}</p>
                <p><strong>Driver:</strong> {tracking.driver_name}</p>
                <p><strong>Status:</strong> {tracking.status}</p>
                <p><strong>Updated:</strong> {tracking.updated_at.strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
            
            <p>Track your order: <a href="https://emonigatsaucee.pythonanywhere.com/track/{order.id}">Click here</a></p>
            <p style="margin-top: 30px;">Best regards,<br><strong>Wegatsaucee Fashion Hub</strong></p>
        </div>
    </body>
    </html>
    """
    return send_email(user.email, f"Order #{order.id} Update - {tracking.location} - Wegatsaucee", html)
```

#### Step 5: Reload Web App
Go to PythonAnywhere dashboard → Web → Reload

---

### Solution 3: Use Mailgun (Alternative)
Similar to SendGrid, also has free tier.

---

## Testing

### On PythonAnywhere Bash Console:
```bash
cd ~/wegatsauceefashionhub
source ~/.virtualenvs/myenv/bin/activate
python test_email_pa.py
```

This will diagnose the exact issue.

---

## Quick Check: Is Gmail SMTP Blocked?

Run this on PythonAnywhere bash:
```bash
python3 -c "import smtplib; s=smtplib.SMTP('smtp.gmail.com',587,timeout=5); print('✓ Port 587 accessible')"
```

If you see an error, Gmail SMTP is blocked → Use SendGrid.

---

## Recommendation

**For production:** Use SendGrid (Solution 2)
- FREE for 100 emails/day
- More reliable than Gmail
- No PythonAnywhere restrictions
- Better deliverability
- Professional email service

**For testing locally:** Gmail SMTP works fine

---

## After Fix

Once emails work, you'll see in error logs:
```
[EMAIL] Sent via SendGrid to user@example.com - Status: 202
```

Instead of:
```
[EMAIL ERROR] Gmail SMTP failed: ...
```
