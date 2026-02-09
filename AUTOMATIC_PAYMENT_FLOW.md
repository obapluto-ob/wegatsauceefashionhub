# Automatic Payment Confirmation Flow

## How It Works

### 1. User Places Order
- User adds items to cart
- Goes to checkout page
- Enters delivery address
- Clicks "Send Order to WhatsApp"
- Order is created with status = "pending"
- User is redirected to WhatsApp to chat with admin

### 2. User Returns to Website
- After chatting with admin on WhatsApp, user might return to the website
- **AUTOMATIC REDIRECT**: When user visits ANY page on the site, they are automatically redirected to the payment-pending page
- This happens for ANY logged-in user with a pending order

### 3. Payment Pending Page
- Shows order details and "Processing Payment" status
- **Auto-updates every 3 seconds** by polling the server
- User doesn't need to refresh or click anything
- Page checks: `/api/order-status/<order_id>` endpoint

### 4. Admin Confirms Payment
- Admin receives WhatsApp message with order details
- Customer sends payment via M-Pesa
- Admin goes to admin panel → Orders
- Changes order status from "pending" to "paid"

### 5. Automatic Confirmation
- Payment-pending page detects status change (within 3 seconds)
- Shows **confetti animation** 🎉
- Displays "Payment Confirmed!" message
- Shows tracking link and dashboard link
- User can now access all pages normally (no more auto-redirect)

## Technical Implementation

### Auto-Redirect System
```python
@app.before_request
def check_pending_payment():
    """Redirect logged-in users with pending orders to payment confirmation page"""
    # Skip for certain routes (API, logout, static files, admin)
    excluded_routes = ['payment_pending', 'api_order_status', 'logout', 'static', 'admin_login', 'admin_logout']
    
    # Only check for logged-in users
    if 'user_id' in session:
        # Check if user has any pending orders
        pending_order = Order.query.filter_by(
            user_id=session['user_id'],
            status='pending'
        ).order_by(Order.created_at.desc()).first()
        
        # If pending order exists, redirect to payment-pending page
        if pending_order:
            return redirect(url_for('payment_pending', order_id=pending_order.id))
```

### Real-Time Status Checking
```javascript
// Check order status every 3 seconds
setInterval(function() {
    fetch(`/api/order-status/${orderId}`)
        .then(response => response.json())
        .then(data => {
            if (data.status !== 'pending') {
                // Payment confirmed! Show confetti and success message
                showConfetti();
                updateUI();
            }
        });
}, 3000);
```

## User Experience Flow

```
1. Checkout → WhatsApp
2. User returns to site → Auto-redirect to payment-pending page
3. Payment-pending page → Auto-updates every 3 seconds
4. Admin confirms payment → Status changes to "paid"
5. Page detects change → Shows confetti + success message
6. User clicks "Track Order" or "Go to Dashboard"
7. No more auto-redirect (order is no longer pending)
```

## Benefits

✅ **No manual refresh needed** - Page auto-updates
✅ **No "Check Status" button needed** - Automatic redirect
✅ **Better UX** - User always sees current payment status
✅ **Real-time feedback** - Updates within 3 seconds
✅ **Clear communication** - User knows exactly what's happening
✅ **Prevents confusion** - Can't access other pages until payment confirmed

## Files Modified

- `app.py` - Added `@app.before_request` decorator for auto-redirect
- `checkout.html` - Simplified to just redirect to WhatsApp
- `payment_pending.html` - Real-time status checking with confetti
- `user_dashboard.html` - Removed "Check Status" button (no longer needed)

## Testing

1. Place an order as a customer
2. Get redirected to WhatsApp
3. Return to website (go to homepage or dashboard)
4. Should automatically see payment-pending page
5. Admin marks order as "paid"
6. Page should show confetti within 3 seconds
7. Click "Go to Dashboard" - should work normally now
