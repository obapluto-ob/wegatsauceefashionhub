# Add these routes to your app.py file

@app.route('/checkout-page')
def checkout_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_user = User.query.get(session['user_id'])
    return render_template('checkout.html', current_user=current_user)

@app.route('/mpesa/callback', methods=['POST'])
def mpesa_callback():
    """Handle M-Pesa payment callback"""
    data = request.get_json()
    
    if data and data.get('Body', {}).get('stkCallback'):
        callback = data['Body']['stkCallback']
        checkout_request_id = callback.get('CheckoutRequestID')
        result_code = callback.get('ResultCode')
        
        # Find order by payment reference
        order = Order.query.filter_by(payment_reference=checkout_request_id).first()
        
        if order:
            if result_code == 0:  # Success
                order.status = 'paid'
                # Clear cart for this user
                # You might want to store cart items in database for better tracking
            else:  # Failed
                order.status = 'failed'
            
            db.session.commit()
    
    return jsonify({'ResultCode': 0, 'ResultDesc': 'Success'})

@app.route('/payment/callback')
def payment_callback():
    """Handle Flutterwave payment callback"""
    tx_ref = request.args.get('tx_ref')
    status = request.args.get('status')
    
    if status == 'successful' and tx_ref:
        # Verify payment with Flutterwave
        result = flutterwave.verify_payment(tx_ref)
        
        if result['success']:
            # Find order by payment reference
            order = Order.query.filter_by(payment_reference=tx_ref).first()
            
            if order:
                order.status = 'paid'
                db.session.commit()
                
                return render_template('payment_success.html', order=order)
    
    return render_template('payment_failed.html')

@app.route('/payment/success/<int:order_id>')
def payment_success(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('payment_success.html', order=order)

@app.route('/payment/failed/<int:order_id>')
def payment_failed(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('payment_failed.html', order=order)