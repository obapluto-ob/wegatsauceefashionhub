#!/usr/bin/env python3
"""
Email Test Script - Diagnose email issues
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from decouple import config

def test_email():
    print("Testing Email Configuration...\n")
    
    # Get config
    email_host = config('EMAIL_HOST')
    email_port = int(config('EMAIL_PORT'))
    email_user = config('EMAIL_USER')
    email_password = config('EMAIL_PASSWORD')
    
    print(f"Host: {email_host}")
    print(f"Port: {email_port}")
    print(f"User: {email_user}")
    print(f"Password: {'*' * len(email_password)}\n")
    
    # Create test email
    msg = MIMEMultipart('alternative')
    msg['From'] = email_user
    msg['To'] = email_user  # Send to yourself
    msg['Subject'] = "Wegatsaucee Email Test"
    
    html = """
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #667eea;">Email System Working!</h2>
        <p>If you receive this email, your email notifications are configured correctly.</p>
        <p><strong>Wegatsaucee Fashion Hub</strong></p>
    </body>
    </html>
    """
    
    html_part = MIMEText(html, 'html')
    msg.attach(html_part)
    
    try:
        print("Connecting to SMTP server...")
        server = smtplib.SMTP(email_host, email_port)
        server.set_debuglevel(1)  # Show detailed output
        
        print("\nStarting TLS...")
        server.starttls()
        
        print("\nLogging in...")
        server.login(email_user, email_password)
        
        print("\nSending test email...")
        server.send_message(msg)
        
        print("\nSUCCESS! Email sent successfully!")
        print(f"Check your inbox: {email_user}")
        
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("\nAUTHENTICATION FAILED!")
        print("Possible issues:")
        print("1. Wrong email or password")
        print("2. App password not enabled")
        print("3. 2FA not enabled on Gmail")
        print("\nFix:")
        print("1. Go to: https://myaccount.google.com/apppasswords")
        print("2. Generate new app password")
        print("3. Update .env file")
        return False
        
    except Exception as e:
        print(f"\nERROR: {e}")
        return False

if __name__ == '__main__':
    test_email()
