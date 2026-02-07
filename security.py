import re
from datetime import datetime, timedelta

# Disposable email domains to block
DISPOSABLE_DOMAINS = [
    'tempmail.com', 'guerrillamail.com', '10minutemail.com', 'throwaway.email',
    'mailinator.com', 'trashmail.com', 'fakeinbox.com', 'yopmail.com',
    'temp-mail.org', 'getnada.com', 'maildrop.cc', 'sharklasers.com'
]

def validate_email_format(email):
    """Check if email has valid format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_disposable_email(email):
    """Check if email is from disposable domain"""
    domain = email.split('@')[1].lower() if '@' in email else ''
    return domain in DISPOSABLE_DOMAINS

def validate_password_strength(password):
    """Check password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain lowercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain number"
    return True, "Password is strong"

def check_honeypot(honeypot_value):
    """Check if honeypot field was filled (bot detection)"""
    return honeypot_value == '' or honeypot_value is None

def check_form_timing(form_start_time):
    """Check if form was filled too quickly (bot detection)"""
    if not form_start_time:
        return False
    try:
        start = datetime.fromisoformat(form_start_time)
        elapsed = (datetime.utcnow() - start).total_seconds()
        return elapsed >= 3  # Must take at least 3 seconds
    except:
        return False

# Failed login tracking
failed_attempts = {}

def check_account_lockout(identifier):
    """Check if account is locked due to failed attempts"""
    if identifier not in failed_attempts:
        return False, 0
    
    attempts = failed_attempts[identifier]
    recent_attempts = [t for t in attempts if datetime.utcnow() - t < timedelta(minutes=15)]
    
    if len(recent_attempts) >= 5:
        return True, len(recent_attempts)
    
    return False, len(recent_attempts)

def record_failed_attempt(identifier):
    """Record a failed login attempt"""
    if identifier not in failed_attempts:
        failed_attempts[identifier] = []
    failed_attempts[identifier].append(datetime.utcnow())

def clear_failed_attempts(identifier):
    """Clear failed attempts after successful login"""
    if identifier in failed_attempts:
        del failed_attempts[identifier]
