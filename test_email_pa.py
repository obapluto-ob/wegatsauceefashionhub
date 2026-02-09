#!/usr/bin/env python3
"""
Email Diagnostic Script for PythonAnywhere
Run this on PythonAnywhere bash console to diagnose email issues
"""

import os
import sys

print("=" * 60)
print("EMAIL DIAGNOSTIC TOOL")
print("=" * 60)

# Check if .env file exists
print("\n1. Checking .env file...")
if os.path.exists('.env'):
    print("   ✓ .env file found")
    with open('.env', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if 'EMAIL' in line and not line.strip().startswith('#'):
                key = line.split('=')[0].strip()
                print(f"   ✓ {key} is set")
else:
    print("   ✗ .env file NOT found!")
    sys.exit(1)

# Load environment variables
print("\n2. Loading environment variables...")
try:
    from decouple import config
    email_user = config('EMAIL_USER', default='NOT_SET')
    email_pass = config('EMAIL_PASSWORD', default='NOT_SET')
    email_host = config('EMAIL_HOST', default='NOT_SET')
    email_port = config('EMAIL_PORT', default='NOT_SET')
    
    print(f"   EMAIL_USER: {email_user}")
    print(f"   EMAIL_HOST: {email_host}")
    print(f"   EMAIL_PORT: {email_port}")
    print(f"   EMAIL_PASSWORD: {'*' * len(email_pass) if email_pass != 'NOT_SET' else 'NOT_SET'}")
except Exception as e:
    print(f"   ✗ Error loading config: {e}")
    sys.exit(1)

# Test SMTP connection
print("\n3. Testing SMTP connection...")
try:
    import smtplib
    server = smtplib.SMTP(email_host, int(email_port), timeout=10)
    print("   ✓ Connected to SMTP server")
    
    server.starttls()
    print("   ✓ TLS started")
    
    server.login(email_user, email_pass)
    print("   ✓ Login successful")
    
    server.quit()
    print("   ✓ Connection closed")
except Exception as e:
    print(f"   ✗ SMTP Error: {type(e).__name__}: {e}")
    print("\n   POSSIBLE CAUSES:")
    print("   - PythonAnywhere blocks Gmail SMTP (port 587)")
    print("   - Wrong email credentials")
    print("   - Gmail 2FA enabled without app password")
    print("   - Gmail 'Less secure apps' disabled")
    sys.exit(1)

# Send test email
print("\n4. Sending test email...")
try:
    from email_notifications import send_email
    
    test_email = input("   Enter test email address: ").strip()
    if not test_email:
        test_email = email_user
    
    result = send_email(
        test_email,
        "Test Email from Wegatsaucee",
        "<h1>Test Successful!</h1><p>Email system is working correctly.</p>"
    )
    
    if result:
        print(f"   ✓ Test email sent to {test_email}")
    else:
        print(f"   ✗ Failed to send test email")
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
