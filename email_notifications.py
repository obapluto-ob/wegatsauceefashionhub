import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from decouple import config

def send_email(to_email, subject, html_content):
    """Send HTML email using Gmail SMTP"""
    try:
        from_email = config('EMAIL_USER')
        password = config('EMAIL_PASSWORD')
        host = config('EMAIL_HOST')
        port = int(config('EMAIL_PORT'))
        
        print(f"[EMAIL DEBUG] Attempting to send to {to_email}")
        print(f"[EMAIL DEBUG] From: {from_email}")
        print(f"[EMAIL DEBUG] Host: {host}:{port}")
        
        msg = MIMEMultipart('alternative')
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        server = smtplib.SMTP(host, port, timeout=10)
        server.set_debuglevel(1)  # Enable debug output
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        print(f"[EMAIL DEBUG] Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email to {to_email}: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def send_order_confirmation(user, order):
    """Send order confirmation email"""
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
    """Send shipping notification email"""
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
    """Send tracking update email"""
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
