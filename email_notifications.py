import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from decouple import config

def send_email(to_email, subject, html_content):
    """Send HTML email using Gmail SMTP"""
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = config('EMAIL_USER')
        msg['To'] = to_email
        msg['Subject'] = subject
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        server = smtplib.SMTP(config('EMAIL_HOST'), int(config('EMAIL_PORT')))
        server.starttls()
        server.login(config('EMAIL_USER'), config('EMAIL_PASSWORD'))
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
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
