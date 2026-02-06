import requests
import json
import base64
from datetime import datetime
from decouple import config
import secrets

class MpesaPayment:
    def __init__(self):
        self.consumer_key = config('MPESA_CONSUMER_KEY', default='')
        self.consumer_secret = config('MPESA_CONSUMER_SECRET', default='')
        self.business_shortcode = config('MPESA_SHORTCODE', default='174379')
        self.passkey = config('MPESA_PASSKEY', default='')
        self.callback_url = config('MPESA_CALLBACK_URL', default='https://yourdomain.com/mpesa/callback')
        
    def get_access_token(self):
        """Get M-Pesa access token"""
        api_url = "https://sandbox-api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        
        credentials = base64.b64encode(f"{self.consumer_key}:{self.consumer_secret}".encode()).decode()
        headers = {"Authorization": f"Basic {credentials}"}
        
        try:
            response = requests.get(api_url, headers=headers)
            return response.json().get('access_token')
        except:
            return None
    
    def stk_push(self, phone_number, amount, order_id):
        """Initiate M-Pesa STK Push"""
        access_token = self.get_access_token()
        if not access_token:
            return {"success": False, "message": "Failed to get access token"}
        
        api_url = "https://sandbox-api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(f"{self.business_shortcode}{self.passkey}{timestamp}".encode()).decode()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "BusinessShortCode": self.business_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": self.business_shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": self.callback_url,
            "AccountReference": f"Order{order_id}",
            "TransactionDesc": f"Payment for Order #{order_id}"
        }
        
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            result = response.json()
            
            if result.get('ResponseCode') == '0':
                return {
                    "success": True,
                    "checkout_request_id": result.get('CheckoutRequestID'),
                    "message": "Payment request sent to phone"
                }
            else:
                return {
                    "success": False,
                    "message": result.get('errorMessage', 'Payment failed')
                }
        except Exception as e:
            return {"success": False, "message": str(e)}

class FlutterwavePayment:
    def __init__(self):
        self.secret_key = config('FLUTTERWAVE_SECRET_KEY', default='')
        self.public_key = config('FLUTTERWAVE_PUBLIC_KEY', default='')
        
    def initiate_payment(self, email, phone, amount, order_id, currency='KES'):
        """Initiate Flutterwave payment"""
        api_url = "https://api.flutterwave.com/v3/payments"
        
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        
        tx_ref = f"turk_trendy_{order_id}_{secrets.token_hex(8)}"
        
        payload = {
            "tx_ref": tx_ref,
            "amount": str(amount),
            "currency": currency,
            "redirect_url": f"{config('BASE_URL', 'http://localhost:5000')}/payment/callback",
            "customer": {
                "email": email,
                "phonenumber": phone,
                "name": "Customer"
            },
            "customizations": {
                "title": "Turk Trendy Shop",
                "description": f"Payment for Order #{order_id}",
                "logo": f"{config('BASE_URL', 'http://localhost:5000')}/static/logo.png"
            }
        }
        
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            result = response.json()
            
            if result.get('status') == 'success':
                return {
                    "success": True,
                    "payment_link": result['data']['link'],
                    "tx_ref": tx_ref
                }
            else:
                return {
                    "success": False,
                    "message": result.get('message', 'Payment initialization failed')
                }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def verify_payment(self, tx_ref):
        """Verify Flutterwave payment"""
        api_url = f"https://api.flutterwave.com/v3/transactions/verify_by_reference?tx_ref={tx_ref}"
        
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(api_url, headers=headers)
            result = response.json()
            
            if result.get('status') == 'success' and result['data']['status'] == 'successful':
                return {
                    "success": True,
                    "amount": result['data']['amount'],
                    "currency": result['data']['currency'],
                    "transaction_id": result['data']['id']
                }
            else:
                return {"success": False, "message": "Payment verification failed"}
        except Exception as e:
            return {"success": False, "message": str(e)}

def detect_payment_method(phone_number, country_code='KE'):
    """Auto-detect best payment method"""
    if country_code in ['KE', 'TZ', 'UG'] and phone_number.startswith(('254', '255', '256')):
        return 'mpesa'
    return 'flutterwave'