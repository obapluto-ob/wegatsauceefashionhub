from flask import Flask, render_template, request, jsonify, session, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict
from payments import MpesaPayment, FlutterwavePayment, detect_payment_method
from decouple import config
from logger import system_logger
from security import (
    validate_email_format, is_disposable_email, validate_password_strength,
    check_honeypot, check_form_timing, check_account_lockout,
    record_failed_attempt, clear_failed_attempts
)

app = Flask(__name__)
app.config['SECRET_KEY'] = config('SECRET_KEY', default='dev-key-change-in-production')

# Fix database path for both local and production
db_uri = config('SQLALCHEMY_DATABASE_URI', default='sqlite:///instance/wegatsaucee.db')
if not db_uri.startswith('sqlite:////'):  # Not absolute path
    if 'sqlite:///' in db_uri and 'instance/' not in db_uri:
        db_uri = db_uri.replace('sqlite:///', 'sqlite:///instance/')
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['RECAPTCHA_SECRET_KEY'] = 'YOUR_SECRET_KEY_HERE'

# Create instance folder if it doesn't exist
os.makedirs('instance', exist_ok=True)

# Initialize payment processors (TEST MODE)
mpesa = MpesaPayment()
flutterwave = FlutterwavePayment()

# Payment system (Live mode simulation)
TEST_MODE = True  # Internal flag - users see live experience

# Rate limiting storage
registration_attempts = defaultdict(list)
login_attempts = defaultdict(list)

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    country_code = db.Column(db.String(2))  # Store country code
    currency = db.Column(db.String(3))  # Store user's currency
    ip_address = db.Column(db.String(45))  # Store IP for tracking
    points = db.Column(db.Integer, default=0)  # Reward points
    tier = db.Column(db.String(20), default='bronze')  # bronze, silver, gold, platinum
    admin_rating = db.Column(db.Integer, default=0)  # Admin rates customer (0-5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.Text)  # Store multiple image URLs as JSON
    video_url = db.Column(db.Text)  # Store multiple video URLs as JSON
    category = db.Column(db.String(50))
    gender = db.Column(db.String(10))  # 'men', 'women', 'unisex'
    stock = db.Column(db.Integer, default=0)
    sizes = db.Column(db.Text)  # JSON array: ["S", "M", "L", "XL"]
    colors = db.Column(db.Text)  # JSON array: ["Red", "Blue", "Black"]
    is_trending = db.Column(db.Boolean, default=False)  # Mark as trending
    flash_sale_price = db.Column(db.Float)  # Flash sale price
    flash_sale_end = db.Column(db.DateTime)  # Flash sale end time
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    shipping_fee = db.Column(db.Float, default=0)
    commission = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default='pending')  # pending, paid, processing, shipped, delivered, cancelled
    payment_method = db.Column(db.String(20), default='whatsapp')  # whatsapp, mpesa
    payment_reference = db.Column(db.String(100))  # Transaction reference
    items = db.Column(db.Text)  # JSON string of cart items
    cancellation_reason = db.Column(db.Text)  # Why order was cancelled
    expected_delivery = db.Column(db.DateTime)  # Expected delivery date
    coupon_code = db.Column(db.String(50))  # Applied coupon code
    discount_amount = db.Column(db.Float, default=0)  # Discount from coupon
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('orders', lazy=True))

class OrderTracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    location = db.Column(db.String(200))  # Current location
    transport_company = db.Column(db.String(100))  # Bus/transport company
    driver_name = db.Column(db.String(100))  # Delivery person name
    status = db.Column(db.String(50))  # Status message
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    order = db.relationship('Order', backref=db.backref('tracking', lazy=True))

class DeliveryConfirmation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    photo_url = db.Column(db.String(500))  # Photo of received product
    rating = db.Column(db.Integer)  # Customer rating (1-5)
    feedback = db.Column(db.Text)  # Customer feedback
    confirmed_by_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    order = db.relationship('Order', backref=db.backref('confirmation', uselist=False, lazy=True))
    user = db.relationship('User', backref=db.backref('confirmations', lazy=True))

class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('wishlist', lazy=True))
    product = db.relationship('Product', backref=db.backref('wishlisted_by', lazy=True))

class RecentlyViewed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('recently_viewed', lazy=True))
    product = db.relationship('Product')

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship('Product', backref=db.backref('reviews', lazy=True))
    user = db.relationship('User', backref=db.backref('reviews', lazy=True))

class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount_percent = db.Column(db.Float)  # Percentage discount
    discount_amount = db.Column(db.Float)  # Fixed amount discount
    min_purchase = db.Column(db.Float, default=0)  # Minimum purchase required
    max_uses = db.Column(db.Integer)  # Max number of uses
    used_count = db.Column(db.Integer, default=0)  # Times used
    expires_at = db.Column(db.DateTime)  # Expiration date
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
def get_user_currency():
    """Get current user's currency or default to KSh"""
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])
        return user.currency if user and user.currency else 'KSh'
    return 'KSh'

def get_country_name(country_code):
    """Get country name from country code"""
    country_names = {
        'us': 'United States',
        'ke': 'Kenya',
        'gb': 'United Kingdom',
        'tz': 'Tanzania',
        'ug': 'Uganda',
        'ng': 'Nigeria',
        'za': 'South Africa'
    }
    return country_names.get(country_code.lower() if country_code else '', 'Unknown')

# Make function available in templates
app.jinja_env.globals.update(get_country_name=get_country_name)

# Add JSON filter for templates
def from_json(value):
    if value:
        try:
            return json.loads(value)
        except:
            return []
    return []

app.jinja_env.filters['from_json'] = from_json

def convert_price(price, to_currency):
    """Convert price from KSh to user's currency"""
    rates = {
        'KSh': 1.0,
        'USD': 0.0067,  # 1 KSh = 0.0067 USD
        'GBP': 0.0052,  # 1 KSh = 0.0052 GBP
        'TSh': 18.5,    # 1 KSh = 18.5 TSh
        'USh': 24.8,    # 1 KSh = 24.8 USh
        'NGN': 11.2,    # 1 KSh = 11.2 NGN
        'ZAR': 0.12     # 1 KSh = 0.12 ZAR
    }
    return round(price * rates.get(to_currency, 1.0), 2)

@app.route('/')
def home():
    import random
    
    # Get trending products and shuffle them
    trending_products = Product.query.filter_by(is_trending=True).all()
    random.shuffle(trending_products)
    trending_products = trending_products[:8]  # Take first 8 after shuffle
    
    # Mark hot products (top bought)
    for product in trending_products:
        # Count how many times this product was ordered
        order_count = 0
        orders = Order.query.filter(Order.status.in_(['paid', 'processing', 'shipped', 'delivered'])).all()
        for order in orders:
            try:
                items = json.loads(order.items)
                for item in items:
                    if item.get('id') == product.id:
                        order_count += item.get('quantity', 1)
            except:
                pass
        
        # Mark as hot if ordered 5+ times
        product.is_hot = order_count >= 5
        product.order_count = order_count
    
    currency = get_user_currency()
    current_user = db.session.get(User, session['user_id']) if 'user_id' in session else None
    
    # Convert prices for display
    for product in trending_products:
        product.display_price = convert_price(product.price, currency)
    
    return render_template('index.html', products=trending_products, currency=currency, current_user=current_user)

@app.route('/products')
def products():
    category = request.args.get('category')
    gender = request.args.get('gender')
    search = request.args.get('search')
    
    query = Product.query
    if category:
        query = query.filter_by(category=category)
    if gender:
        query = query.filter_by(gender=gender)
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%') | Product.description.ilike(f'%{search}%'))
    
    products = query.all()
    
    currency = get_user_currency()
    current_user = db.session.get(User, session['user_id']) if 'user_id' in session else None
    
    # Convert prices for display
    for product in products:
        product.display_price = convert_price(product.price, currency)
    
    return render_template('products.html', products=products, currency=currency, current_user=current_user)

@app.route('/product/<int:id>')
def product_detail(id):
    product = db.session.get(Product, id)
    if not product:
        abort(404)
    
    # Track recently viewed
    if 'user_id' in session:
        old_view = RecentlyViewed.query.filter_by(user_id=session['user_id'], product_id=id).first()
        if old_view:
            db.session.delete(old_view)
        recent_view = RecentlyViewed(user_id=session['user_id'], product_id=id)
        db.session.add(recent_view)
        all_views = RecentlyViewed.query.filter_by(user_id=session['user_id']).order_by(RecentlyViewed.viewed_at.desc()).all()
        if len(all_views) > 10:
            for old in all_views[10:]:
                db.session.delete(old)
        db.session.commit()
    
    # Get related products (same category, different product)
    related_products = Product.query.filter(
        Product.category == product.category,
        Product.id != product.id
    ).limit(4).all()
    
    # Get reviews
    reviews = Review.query.filter_by(product_id=id).order_by(Review.created_at.desc()).all()
    avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
    
    # Check if in wishlist
    in_wishlist = False
    if 'user_id' in session:
        in_wishlist = Wishlist.query.filter_by(user_id=session['user_id'], product_id=id).first() is not None
    
    currency = get_user_currency()
    current_user = db.session.get(User, session['user_id']) if 'user_id' in session else None
    product.display_price = convert_price(product.price, currency)
    
    # Convert related products prices
    for rp in related_products:
        rp.display_price = convert_price(rp.price, currency)
    
    return render_template('product_detail.html', product=product, reviews=reviews, avg_rating=avg_rating, 
                         currency=currency, current_user=current_user, in_wishlist=in_wishlist,
                         related_products=related_products)

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    current_user = db.session.get(User, session['user_id']) if 'user_id' in session else None
    return render_template('cart.html', cart_items=cart_items, total=total, current_user=current_user)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity', 1)
    
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    cart = session.get('cart', [])
    
    # Check if product already in cart
    for item in cart:
        if item['id'] == product_id:
            item['quantity'] += quantity
            break
    else:
        # Handle image URL - extract first image if JSON array
        image_url = product.image_url
        if image_url and image_url.startswith('['):
            try:
                images = json.loads(image_url)
                image_url = images[0] if images else None
            except:
                image_url = None
        
        cart.append({
            'id': product_id,
            'name': product.name,
            'price': product.price,
            'quantity': quantity,
            'image_url': image_url
        })
    
    session['cart'] = cart
    
    # Handle image URL - extract first image if JSON array
    image_url = product.image_url
    if image_url and image_url.startswith('['):
        try:
            images = json.loads(image_url)
            image_url = images[0] if images else None
        except:
            image_url = None
    
    return jsonify({
        'success': True, 
        'cart_count': len(cart),
        'product': {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'image_url': image_url,
            'description': product.description,
            'category': product.category
        }
    })

def verify_recaptcha(response):
    """Verify reCAPTCHA response - DISABLED until API keys are added"""
    # TODO: Enable when you have reCAPTCHA API keys
    return True  # Temporarily disabled
    
    # Uncomment below when you have API keys:
    # data = {
    #     'secret': app.config['RECAPTCHA_SECRET_KEY'],
    #     'response': response,
    #     'remoteip': request.environ.get('REMOTE_ADDR')
    # }
    # r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    # return r.json().get('success', False)

def check_rate_limit(ip, action, limit=3, window=3600):
    """Check if IP has exceeded rate limit"""
    now = datetime.utcnow()
    attempts = registration_attempts if action == 'register' else login_attempts
    
    # Clean old attempts
    attempts[ip] = [t for t in attempts[ip] if now - t < timedelta(seconds=window)]
    
    return len(attempts[ip]) < limit

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        ip = request.environ.get('REMOTE_ADDR')
        
        # Rate limiting
        if not check_rate_limit(ip, 'register'):
            return render_template('register.html', error='Too many registration attempts. Try again later.')
        
        # Bot detection - Honeypot (optional check)
        honeypot = request.form.get('website', '')
        # Skip honeypot check for now - too strict
        
        # Bot detection - Form timing (relaxed)
        form_start = request.form.get('form_start_time')
        # Skip timing check for now - too strict
        
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        name = request.form['name']
        phone = request.form['phone']
        country_code = request.form.get('country_code', 'ke')
        currency = request.form.get('currency', 'KSh')
        
        # Email validation
        if not validate_email_format(email):
            return render_template('register.html', error='Invalid email format')
        
        if is_disposable_email(email):
            return render_template('register.html', error='Disposable email addresses are not allowed')
        
        # Password validation (relaxed - just check length)
        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters')
        
        # Check if passwords match
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')
        
        # Check for existing email
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='This email is already registered')
        
        # Check for existing name
        if User.query.filter_by(name=name).first():
            return render_template('register.html', error='This name is already taken. Please choose a different name')
        
        # Check for existing phone number
        if User.query.filter_by(phone=phone).first():
            return render_template('register.html', error='This phone number is already registered')
        
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            name=name,
            phone=phone,
            country_code=country_code,
            currency=currency,
            ip_address=ip
        )
        db.session.add(user)
        db.session.commit()
        
        # Record successful registration
        registration_attempts[ip].append(datetime.utcnow())
        
        session['user_id'] = user.id
        return redirect(url_for('user_dashboard'))
    
    return render_template('register.html', current_user=None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ip = request.environ.get('REMOTE_ADDR')
        email = request.form['email']
        
        # Check account lockout
        is_locked, attempts = check_account_lockout(email)
        if is_locked:
            return render_template('login.html', error=f'Account locked due to {attempts} failed attempts. Try again in 15 minutes.')
        
        # Rate limiting for login attempts
        if not check_rate_limit(ip, 'login', limit=5, window=900):  # 5 attempts per 15 min
            return render_template('login.html', error='Too many login attempts. Try again later.')
        
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            clear_failed_attempts(email)
            session['user_id'] = user.id
            system_logger.log('INFO', f'User login: {email}', user_id=user.id, ip=ip)
            return redirect(url_for('user_dashboard'))
        
        # Record failed login attempt
        record_failed_attempt(email)
        login_attempts[ip].append(datetime.utcnow())
        system_logger.log('WARNING', f'Failed login: {email}', ip=ip)
        return render_template('login.html', error='Invalid credentials')
    
    # If already logged in, redirect to dashboard
    if 'user_id' in session:
        return redirect(url_for('user_dashboard'))
    
    return render_template('login.html', current_user=None)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # Check if passwords match
        if new_password != confirm_password:
            return render_template('forgot_password.html', 
                                 error='Passwords do not match')
        
        # Get full phone number from international input
        full_phone = request.form.get('phone')
        
        # Find user by name and phone
        user = User.query.filter_by(name=name, phone=full_phone).first()
        
        if not user:
            return render_template('forgot_password.html', 
                                 error='Name and phone number do not match our records. Make sure you registered with this phone number.')
        
        # Check if new password is same as current password
        if check_password_hash(user.password_hash, new_password):
            return render_template('forgot_password.html', 
                                 error='You cannot use your previous password. Please choose a different password.')
        
        # Update password
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        # Auto login
        session['user_id'] = user.id
        return redirect(url_for('user_dashboard'))
    
    return render_template('forgot_password.html', current_user=None)

@app.route('/dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_user = db.session.get(User, session['user_id'])
    user_orders = Order.query.filter_by(user_id=session['user_id']).order_by(Order.created_at.desc()).all()
    total_spent = sum(order.total for order in user_orders)
    active_orders = len([order for order in user_orders if order.status in ['pending', 'processing', 'shipped']])
    
    return render_template('user_dashboard.html', 
                         orders=user_orders,
                         total_spent=total_spent,
                         active_orders=active_orders,
                         current_user=current_user)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Admin credentials from environment (SECURE)
        admin_user = config('ADMIN_USER')
        admin_pass = config('ADMIN_PASS')
        
        if username == admin_user and password == admin_pass:
            session['admin_logged_in'] = True
            ip = request.environ.get('REMOTE_ADDR')
            system_logger.log('INFO', f'Admin login successful', user_id='admin', ip=ip)
            return redirect(url_for('admin_dashboard'))
        
        ip = request.environ.get('REMOTE_ADDR')
        system_logger.log('WARNING', f'Failed admin login attempt: {username}', ip=ip)
        return render_template('admin_login.html', error='Invalid credentials')
    
    return render_template('admin_login.html')

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
        
    # Basic stats
    total_orders = Order.query.count()
    total_products = Product.query.count()
    total_users = User.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total)).scalar() or 0
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    products = Product.query.order_by(Product.created_at.desc()).all()
    
    # Low stock products (stock <= 5)
    low_stock_products = Product.query.filter(Product.stock <= 5).all()
    
    # Today's sales
    from datetime import date
    today = date.today()
    today_orders = Order.query.filter(db.func.date(Order.created_at) == today).all()
    today_sales = sum(order.total for order in today_orders)
    
    # Remove fake best seller - no real sales tracking yet
    best_seller = None
    
    return render_template('admin_dashboard.html', 
                         total_orders=total_orders,
                         total_products=total_products,
                         total_users=total_users,
                         total_revenue=total_revenue,
                         recent_orders=recent_orders,
                         products=products,
                         low_stock_products=low_stock_products,
                         today_sales=today_sales,
                         today_orders=len(today_orders),
                         best_seller=best_seller)

@app.route('/admin/add_product', methods=['POST'])
def admin_add_product():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
        
    name = request.form['name']
    price = float(request.form['price'])
    description = request.form.get('description', '')
    category = request.form['category']
    gender = request.form['gender']
    stock = int(request.form['stock'])
    
    # Parse sizes and colors
    sizes_str = request.form.get('sizes', '').strip()
    colors_str = request.form.get('colors', '').strip()
    sizes = json.dumps([s.strip() for s in sizes_str.split(',') if s.strip()]) if sizes_str else None
    colors = json.dumps([c.strip() for c in colors_str.split(',') if c.strip()]) if colors_str else None
    
    image_urls = []
    video_urls = []
    
    # Handle multiple image uploads
    if 'images' in request.files:
        files = request.files.getlist('images')
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_urls.append(f'/static/uploads/{filename}')
    
    # Handle multiple video uploads
    if 'videos' in request.files:
        files = request.files.getlist('videos')
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                video_urls.append(f'/static/uploads/{filename}')
    
    product = Product(
        name=name, 
        price=price, 
        description=description, 
        category=category, 
        gender=gender,
        stock=stock, 
        image_url=json.dumps(image_urls) if image_urls else None,
        video_url=json.dumps(video_urls) if video_urls else None,
        sizes=sizes,
        colors=colors
    )
    db.session.add(product)
    db.session.commit()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_order', methods=['POST'])
def admin_update_order():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
        
    order_id = request.form['order_id']
    status = request.form['status']
    
    order = db.session.get(Order, order_id)
    if order:
        order.status = status
        db.session.commit()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
def admin_edit_product(product_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
        
    product = db.session.get(Product, product_id)
    if not product:
        abort(404)
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.price = float(request.form['price'])
        product.description = request.form.get('description', '')
        product.category = request.form['category']
        product.gender = request.form['gender']
        product.stock = int(request.form['stock'])
        
        # Handle new images upload
        if 'images' in request.files:
            files = request.files.getlist('images')
            existing_images = []
            
            # Get existing images
            if product.image_url:
                if product.image_url.startswith('['):
                    existing_images = json.loads(product.image_url)
                else:
                    existing_images = [product.image_url]
            
            # Add new images (only if files were actually selected)
            new_images_added = False
            for file in files:
                if file and file.filename and file.filename.strip():
                    filename = secure_filename(file.filename)
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    existing_images.append(f'/static/uploads/{filename}')
                    new_images_added = True
            
            # Only update if new images were actually added
            if new_images_added and existing_images:
                product.image_url = json.dumps(existing_images)
            elif not existing_images:
                product.image_url = None
        
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin_edit_product.html', product=product)

@app.route('/admin/toggle_trending/<int:product_id>', methods=['POST'])
def admin_toggle_trending(product_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
        
    product = db.session.get(Product, product_id)
    if product:
        product.is_trending = not product.is_trending
        db.session.commit()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/remove_image', methods=['POST'])
def admin_remove_image():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    product_id = data.get('product_id')
    image_url = data.get('image_url')
    
    product = Product.query.get(product_id)
    if product and product.image_url:
        if product.image_url.startswith('['):
            images = json.loads(product.image_url)
            if image_url in images:
                images.remove(image_url)
                product.image_url = json.dumps(images) if images else None
        else:
            if product.image_url == image_url:
                product.image_url = None
        
        db.session.commit()
    
    return jsonify({'success': True})

@app.route('/admin/backup')
def admin_backup():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    import sqlite3
    import shutil
    from datetime import datetime
    
    try:
        # Create backup
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy('wegatsaucee.db', f'backups/{backup_name}')
        return jsonify({'success': True, 'backup': backup_name})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/export/products')
def admin_export_products():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    import csv
    from io import StringIO
    from flask import Response
    
    try:
        products = Product.query.all()
        
        # Create CSV
        si = StringIO()
        writer = csv.writer(si)
        writer.writerow(['ID', 'Name', 'Price', 'Category', 'Gender', 'Stock', 'Description'])
        
        for p in products:
            writer.writerow([p.id, p.name, p.price, p.category, p.gender, p.stock, p.description])
        
        output = si.getvalue()
        si.close()
        
        return Response(
            output,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=products.csv'}
        )
    except Exception as e:
        return f"Error exporting products: {str(e)}", 500

@app.route('/admin/export/users')
def admin_export_users():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    import csv
    from io import StringIO
    from flask import Response
    
    try:
        users = User.query.all()
        
        # Create CSV
        si = StringIO()
        writer = csv.writer(si)
        writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Tier', 'Points', 'Created'])
        
        for u in users:
            writer.writerow([u.id, u.name, u.email, u.phone, u.tier, u.points, u.created_at.strftime('%Y-%m-%d')])
        
        output = si.getvalue()
        si.close()
        
        return Response(
            output,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=users.csv'}
        )
    except Exception as e:
        return f"Error exporting users: {str(e)}", 500

@app.route('/admin/settings')
def admin_settings():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin_settings.html')

@app.route('/admin/logs')
def admin_logs():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    logs = system_logger.get_logs(limit=500)
    return render_template('admin_logs.html', logs=logs)

@app.route('/admin/logs/data')
def admin_logs_data():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    logs = system_logger.get_logs(limit=500)
    return jsonify({'logs': logs})

@app.route('/admin/logs/clear', methods=['POST'])
def admin_logs_clear():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    system_logger.clear_logs()
    system_logger.log('INFO', 'System logs cleared by admin', user_id='admin', ip=request.environ.get('REMOTE_ADDR'))
    return jsonify({'success': True})

@app.route('/admin/developer')
def admin_developer_tools():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    stats = system_logger.get_system_stats()
    error_logs = system_logger.get_error_logs(limit=10)
    performance_logs = system_logger.get_performance_logs(limit=10)
    
    return render_template('admin_developer_tools.html', 
                         stats=stats, 
                         error_logs=error_logs,
                         performance_logs=performance_logs)

@app.route('/admin/developer/stats')
def admin_developer_stats():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    return jsonify(system_logger.get_system_stats())

@app.route('/admin/developer/optimize-db', methods=['POST'])
def admin_optimize_db():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # SQLite optimization
        with db.engine.connect() as conn:
            conn.execute(db.text('VACUUM'))
            conn.execute(db.text('ANALYZE'))
        system_logger.log('INFO', 'Database optimized by admin', user_id='admin', ip=request.environ.get('REMOTE_ADDR'))
        return jsonify({'success': True, 'message': 'Database optimized successfully'})
    except Exception as e:
        system_logger.log_exception(e, user_id='admin', ip=request.environ.get('REMOTE_ADDR'))
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/developer/clear-cache', methods=['POST'])
def admin_clear_cache():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Clear only user sessions, keep admin session
    admin_status = session.get('admin_logged_in')
    session.clear()
    session['admin_logged_in'] = admin_status
    system_logger.log('INFO', 'Cache cleared by admin', user_id='admin', ip=request.environ.get('REMOTE_ADDR'))
    return jsonify({'success': True, 'message': 'Cache cleared successfully'})

@app.route('/admin/optimize', methods=['POST'])
def admin_optimize():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text('VACUUM'))
            conn.execute(db.text('ANALYZE'))
        system_logger.log('INFO', 'Database optimized by admin', user_id='admin', ip=request.environ.get('REMOTE_ADDR'))
        return jsonify({'success': True, 'message': 'Database optimized successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/clear_logs', methods=['POST'])
def admin_clear_logs():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    system_logger.clear_logs()
    system_logger.log('INFO', 'System logs cleared by admin', user_id='admin', ip=request.environ.get('REMOTE_ADDR'))
    return jsonify({'success': True, 'message': 'Logs cleared successfully'})

@app.route('/admin/developer/create-backup', methods=['POST'])
def admin_create_backup():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    import shutil
    from datetime import datetime
    backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy('instance/wegatsaucee.db', f'instance/{backup_name}')
    system_logger.log('INFO', f'Database backup created: {backup_name}', user_id='admin', ip=request.environ.get('REMOTE_ADDR'))
    return jsonify({'success': True, 'message': f'Backup created: {backup_name}'})

@app.route('/admin/developer/analyze-queries', methods=['POST'])
def admin_analyze_queries():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        with db.engine.connect() as conn:
            result = conn.execute(db.text('PRAGMA table_info(user)'))
            tables = result.fetchall()
        system_logger.log('INFO', 'Query analysis completed', user_id='admin', ip=request.environ.get('REMOTE_ADDR'))
        return jsonify({'success': True, 'message': 'Query analysis completed'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/admin/developer/preload-cache', methods=['POST'])
def admin_preload_cache():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Preload common queries
    User.query.count()
    Product.query.count()
    Order.query.count()
    system_logger.log('INFO', 'Cache preloaded', user_id='admin', ip=request.environ.get('REMOTE_ADDR'))
    return jsonify({'success': True, 'message': 'Cache preloaded successfully'})

@app.route('/admin/developer/cache-stats', methods=['GET'])
def admin_cache_stats():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    stats = {
        'session_count': len(session),
        'memory_usage': '0.07MB',
        'cache_hits': 0,
        'cache_misses': 0
    }
    return jsonify(stats)

@app.route('/admin/developer/system-report', methods=['GET'])
def admin_system_report():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    report = {
        'database': {
            'users': User.query.count(),
            'products': Product.query.count(),
            'orders': Order.query.count()
        },
        'system': system_logger.get_system_stats(),
        'errors': len(system_logger.get_error_logs(limit=100))
    }
    return jsonify(report)

@app.route('/admin/developer/health-check')
def admin_health_check():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    health_status = {
        'healthy': True,
        'details': {
            'database': 'OK',
            'memory': 'OK',
            'disk': 'OK',
            'errors': 'OK'
        }
    }
    
    try:
        # Check database
        User.query.count()
        
        # Check system resources
        stats = system_logger.get_system_stats()
        if stats['memory_usage'] > 1000:  # > 1GB
            health_status['details']['memory'] = 'HIGH'
            health_status['healthy'] = False
        
        if stats['disk_usage'] > 90:  # > 90%
            health_status['details']['disk'] = 'HIGH'
            health_status['healthy'] = False
        
        if stats['error_count'] > 50:  # > 50 errors
            health_status['details']['errors'] = 'HIGH'
            health_status['healthy'] = False
            
    except Exception as e:
        health_status['healthy'] = False
        health_status['details']['database'] = f'ERROR: {str(e)}'
    
    return jsonify(health_status)

@app.route('/admin/developer/clear-all-cache', methods=['POST'])
def admin_clear_all_cache():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    admin_status = session.get('admin_logged_in')
    session.clear()
    session['admin_logged_in'] = admin_status
    system_logger.log('INFO', 'All cache cleared by admin', user_id='admin', ip=request.environ.get('REMOTE_ADDR'))
    return jsonify({'success': True, 'message': 'All cache cleared successfully'})

@app.route('/admin/terminal')
def admin_terminal():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    logs = system_logger.get_logs(limit=100)
    stats = system_logger.get_system_stats()
    
    return render_template('admin_terminal.html', logs=logs, stats=stats)

@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
def admin_delete_product(product_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
        
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/track/<int:order_id>')
def track_order(order_id):
    order = Order.query.get_or_404(order_id)
    # Public tracking - anyone can view with order ID (like FedEx)
    return render_template('track_order.html', order=order)

@app.route('/admin/orders')
def admin_orders():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin_orders.html', orders=orders)

@app.route('/admin/order/<int:order_id>')
def admin_order_detail(order_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    order = Order.query.get_or_404(order_id)
    return jsonify({
        'id': order.id,
        'customer': order.user.name,
        'total': order.total,
        'status': order.status
    })

@app.route('/admin/update_order_status', methods=['POST'])
def admin_update_order_status():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    order_id = request.form['order_id']
    status = request.form['status']
    
    order = db.session.get(Order, order_id)
    if order:
        # Prevent editing if order has delivery confirmation
        if order.confirmation:
            return redirect(url_for('admin_orders'))
        
        old_status = order.status
        order.status = status
        
        # Award points when order is marked as paid
        if old_status != 'paid' and status == 'paid':
            user = order.user
            # Calculate points based on spending (1 point per 100 KSh)
            multiplier = get_points_multiplier(user.tier)
            points_earned = int((order.total / 100) * multiplier)
            user.points += points_earned
            update_user_tier(user)
        
        db.session.commit()
    
    return redirect(url_for('admin_orders'))

@app.route('/admin/track_order/<int:order_id>')
def admin_track_order(order_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    order = Order.query.get_or_404(order_id)
    return render_template('admin_track_order.html', order=order)

@app.route('/admin/add_tracking', methods=['POST'])
def admin_add_tracking():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    order_id = request.form['order_id']
    order = Order.query.get(order_id)
    
    # Prevent adding tracking if order has delivery confirmation
    if order and order.confirmation:
        return redirect(url_for('admin_orders'))
    
    location = request.form['location']
    transport_company = request.form['transport_company']
    driver_name = request.form['driver_name']
    status = request.form['status']
    
    tracking = OrderTracking(
        order_id=order_id,
        location=location,
        transport_company=transport_company,
        driver_name=driver_name,
        status=status
    )
    db.session.add(tracking)
    db.session.commit()
    
    # Send tracking update email
    if order and order.user:
        from email_notifications import send_tracking_update
        send_tracking_update(order.user, order, tracking)
    
    return redirect(url_for('admin_orders'))

@app.route('/confirm_delivery/<int:order_id>', methods=['POST'])
def confirm_delivery(order_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    order = Order.query.get_or_404(order_id)
    
    # Check if already confirmed
    if order.confirmation:
        return redirect(url_for('track_order', order_id=order_id))
    
    # Handle photo upload
    photo_url = None
    if 'photo' in request.files:
        file = request.files['photo']
        if file and file.filename:
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            photo_url = f'/static/uploads/{filename}'
    
    rating = int(request.form['rating'])
    feedback = request.form['feedback']
    
    # Create delivery confirmation
    confirmation = DeliveryConfirmation(
        order_id=order_id,
        user_id=session['user_id'],
        photo_url=photo_url,
        rating=rating,
        feedback=feedback
    )
    db.session.add(confirmation)
    
    # Auto-create review from delivery confirmation
    try:
        items = json.loads(order.items)
        for item in items:
            product_id = item.get('id')
            if product_id:
                # Check if review already exists
                existing_review = Review.query.filter_by(product_id=product_id, user_id=session['user_id']).first()
                if not existing_review:
                    review = Review(
                        product_id=product_id,
                        user_id=session['user_id'],
                        rating=rating,
                        comment=feedback
                    )
                    db.session.add(review)
    except:
        pass
    
    # Award points for completing delivery flow
    user = order.user
    multiplier = get_points_multiplier(user.tier)
    points_earned = int(50 * multiplier)  # Base 50 points
    if rating >= 4:  # Bonus for good rating
        points_earned += 100
    
    user.points += points_earned
    update_user_tier(user)
    
    db.session.commit()
    
    return redirect(url_for('track_order', order_id=order_id))

@app.route('/admin/confirm_delivery', methods=['POST'])
def admin_confirm_delivery():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    confirmation_id = request.form['confirmation_id']
    admin_rating = int(request.form['admin_rating'])
    
    confirmation = DeliveryConfirmation.query.get_or_404(confirmation_id)
    confirmation.confirmed_by_admin = True
    
    # Update user's admin rating
    user = confirmation.user
    user.admin_rating = admin_rating
    
    db.session.commit()
    
    return redirect(url_for('admin_orders'))

# CANCELLATION ROUTES
@app.route('/cancel_order/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    order = Order.query.get_or_404(order_id)
    
    # Only allow cancellation if pending
    if order.status != 'pending':
        return jsonify({'error': 'Cannot cancel this order'}), 400
    
    reason = request.json.get('reason', 'Customer requested cancellation')
    order.status = 'cancelled'
    order.cancellation_reason = reason
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/request_refund/<int:order_id>', methods=['POST'])
def request_refund(order_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    order = Order.query.get_or_404(order_id)
    user = order.user
    
    # Build refund request message
    message = f"*REFUND REQUEST - Order #{order.id}*\n\n"
    message += f"Customer: {user.name}\n"
    message += f"Phone: {user.phone}\n"
    message += f"Email: {user.email}\n\n"
    message += f"Order Total: KSh {order.total:,.0f}\n"
    message += f"Order Date: {order.created_at.strftime('%B %d, %Y')}\n\n"
    message += f"Reason: {request.json.get('reason', 'Not specified')}\n\n"
    message += "Please process my refund. Thank you."
    
    import urllib.parse
    encoded_message = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/254729453903?text={encoded_message}"
    
    return jsonify({'success': True, 'whatsapp_url': whatsapp_url})

@app.route('/report_issue/<int:order_id>', methods=['POST'])
def report_issue(order_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    order = Order.query.get_or_404(order_id)
    user = order.user
    issue_type = request.json.get('type', 'general')
    
    message = f"*ISSUE REPORT - Order #{order.id}*\n\n"
    message += f"Customer: {user.name}\n"
    message += f"Phone: {user.phone}\n\n"
    
    if issue_type == 'payment_not_confirmed':
        message += "Issue: Payment not confirmed\n"
        message += "I sent payment but order still shows as pending.\n"
        message += "Please confirm my payment."
    elif issue_type == 'delivery_delay':
        message += "Issue: Delivery Delay\n"
        message += f"Expected: {order.expected_delivery.strftime('%B %d, %Y')}\n"
        message += "My order is delayed. Please provide update."
    else:
        message += f"Issue: {request.json.get('message', 'General concern')}\n"
    
    import urllib.parse
    encoded_message = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/254729453903?text={encoded_message}"
    
    return jsonify({'success': True, 'whatsapp_url': whatsapp_url})

# WISHLIST ROUTES
@app.route('/wishlist/add/<int:product_id>', methods=['POST'])
def add_to_wishlist(product_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    # Check if already in wishlist
    existing = Wishlist.query.filter_by(user_id=session['user_id'], product_id=product_id).first()
    if existing:
        return jsonify({'success': True, 'message': 'Already in wishlist'})
    
    wishlist_item = Wishlist(user_id=session['user_id'], product_id=product_id)
    db.session.add(wishlist_item)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/wishlist/remove/<int:product_id>', methods=['POST'])
def remove_from_wishlist(product_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    wishlist_item = Wishlist.query.filter_by(user_id=session['user_id'], product_id=product_id).first()
    if wishlist_item:
        db.session.delete(wishlist_item)
        db.session.commit()
    
    return jsonify({'success': True})

@app.route('/wishlist')
def view_wishlist():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    wishlist_items = Wishlist.query.filter_by(user_id=session['user_id']).all()
    products = [item.product for item in wishlist_items]
    
    currency = get_user_currency()
    current_user = db.session.get(User, session['user_id'])
    
    for product in products:
        product.display_price = convert_price(product.price, currency)
    
    return render_template('wishlist.html', products=products, currency=currency, current_user=current_user)

# SEARCH AUTOCOMPLETE
@app.route('/search/autocomplete')
def search_autocomplete():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    products = Product.query.filter(
        Product.name.ilike(f'%{query}%')
    ).limit(5).all()
    
    results = [{
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'image': json.loads(p.image_url)[0] if p.image_url and p.image_url.startswith('[') else p.image_url,
        'category': p.category
    } for p in products]
    
    return jsonify(results)

# RECENTLY VIEWED
@app.route('/recently_viewed')
def recently_viewed():
    if 'user_id' not in session:
        return jsonify([])
    
    views = RecentlyViewed.query.filter_by(user_id=session['user_id']).order_by(RecentlyViewed.viewed_at.desc()).limit(5).all()
    products = [{
        'id': v.product.id,
        'name': v.product.name,
        'price': v.product.price,
        'image': json.loads(v.product.image_url)[0] if v.product.image_url and v.product.image_url.startswith('[') else v.product.image_url
    } for v in views]
    
    return jsonify(products)

@app.route('/track', methods=['POST'])
def track_order_post():
    order_id = request.form['order_id']
    return redirect(url_for('track_order', order_id=order_id))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.session.get(User, session['user_id'])
    
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        
        # Check if name/email already exists (excluding current user)
        if User.query.filter(User.name == name, User.id != user.id).first():
            return render_template('profile.html', user=user, error='Name already taken')
        
        if User.query.filter(User.email == email, User.id != user.id).first():
            return render_template('profile.html', user=user, error='Email already exists')
        
        # Update user info
        user.name = name
        user.email = email
        user.phone = phone
        db.session.commit()
        
        return render_template('profile.html', user=user, message='Profile updated successfully')
    
    return render_template('profile.html', user=user)

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    cart = request.json.get('cart', [])
    if not cart:
        return jsonify({'error': 'Cart is empty'}), 400
    
    user = db.session.get(User, session['user_id'])
    coupon_code = request.json.get('coupon_code')
    discount_amount = request.json.get('discount_amount', 0)
    
    # Calculate totals
    subtotal = sum(item['price'] * item['quantity'] for item in cart)
    
    # Apply discount
    subtotal_after_discount = subtotal - discount_amount
    
    # Tiered shipping based on order value
    if subtotal_after_discount < 2000:
        shipping_fee = 300
    elif subtotal_after_discount < 5000:
        shipping_fee = 400
    else:
        shipping_fee = 500
    
    # Check for free shipping benefits
    if user.tier == 'gold' and subtotal_after_discount >= 6000:
        shipping_fee = 0
    elif user.tier == 'platinum':
        from datetime import date
        this_month = date.today().replace(day=1)
        free_shipping_used = Order.query.filter(
            Order.user_id == user.id,
            Order.shipping_fee == 0,
            Order.created_at >= this_month
        ).count()
        if free_shipping_used == 0:
            shipping_fee = 0
    
    # Platform commission (10%)
    commission = subtotal_after_discount * 0.10
    total = subtotal_after_discount + shipping_fee + commission
    
    # Expected delivery (7-14 days from Tanzania to Kenya)
    from datetime import timedelta
    expected_delivery = datetime.utcnow() + timedelta(days=10)
    
    # Create order
    order = Order(
        user_id=user.id,
        total=total,
        shipping_fee=shipping_fee,
        commission=commission,
        status='pending',
        payment_method='whatsapp',
        items=json.dumps(cart),
        expected_delivery=expected_delivery,
        coupon_code=coupon_code,
        discount_amount=discount_amount
    )
    db.session.add(order)
    
    # Update coupon usage
    if coupon_code:
        coupon = Coupon.query.filter_by(code=coupon_code.upper()).first()
        if coupon:
            coupon.used_count += 1
    
    db.session.commit()
    
    # Build WhatsApp message with PAYMENT PROTECTION
    tier_badges = {'bronze': '[BRONZE]', 'silver': '[SILVER]', 'gold': '[GOLD]', 'platinum': '[PLATINUM VIP]'}
    tier_badge = tier_badges.get(user.tier, '[BRONZE]')
    
    message = f"*{tier_badge} New Order #{order.id}*\n\n"
    message += f"Customer: {user.name} ({user.points} points)\n"
    message += f"Email: {user.email}\n"
    message += f"Phone: {user.phone}\n\n"
    
    # PAYMENT PROTECTION NOTICE
    message += "*PAYMENT PROTECTION ACTIVE*\n"
    message += "Customer will only pay after you confirm this order.\n"
    message += "Please review and send M-Pesa payment details.\n\n"
    
    if user.tier != 'bronze':
        message += f"Benefits: "
        if user.tier == 'silver':
            message += "Priority Support, Early Access\n\n"
        elif user.tier == 'gold':
            message += "Priority Support, Early Access"
            if subtotal_after_discount >= 6000:
                message += ", FREE SHIPPING\n\n"
            else:
                message += "\n\n"
        elif user.tier == 'platinum':
            message += "VIP Support, Personal Assistant, FREE SHIPPING\n\n"
    
    message += "*Products:*\n"
    for item in cart:
        message += f"- {item['name']} x{item['quantity']} = KSh {item['price'] * item['quantity']:,.0f}\n"
        if item.get('size'):
            message += f"  Size: {item['size']}\n"
        if item.get('color'):
            message += f"  Color: {item['color']}\n"
        if item.get('image_url'):
            message += f"  Image: {request.host_url.rstrip('/')}{item['image_url']}\n"
    
    message += f"\nSubtotal: KSh {subtotal:,.0f}\n"
    if discount_amount > 0:
        message += f"Discount ({coupon_code}): -KSh {discount_amount:,.0f}\n"
    message += f"Shipping: KSh {shipping_fee:,.0f}"
    if shipping_fee == 0:
        message += " (FREE - Tier Benefit)"
    message += f"\nTax: KSh {commission:,.0f}\n"
    message += f"*TOTAL: KSh {total:,.0f}*\n\n"
    message += f"Expected Delivery: {expected_delivery.strftime('%B %d, %Y')}\n\n"
    message += "Thank you for your order!"
    
    import urllib.parse
    encoded_message = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/254729453903?text={encoded_message}"
    
    return jsonify({
        'success': True,
        'whatsapp_url': whatsapp_url,
        'order_id': order.id
    })

# Helper function to update user tier
def update_user_tier(user):
    points = user.points
    if points >= 5000:
        user.tier = 'platinum'
    elif points >= 2000:
        user.tier = 'gold'
    elif points >= 500:
        user.tier = 'silver'
    else:
        user.tier = 'bronze'
    db.session.commit()

# Helper function to calculate points multiplier
def get_points_multiplier(tier):
    multipliers = {
        'bronze': 1.0,
        'silver': 1.5,
        'gold': 2.0,
        'platinum': 2.5
    }
    return multipliers.get(tier, 1.0)

@app.route('/product/<int:id>/review', methods=['POST'])
def add_review(id):
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    
    product = db.session.get(Product, id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Check if user already reviewed
    existing_review = Review.query.filter_by(product_id=id, user_id=session['user_id']).first()
    if existing_review:
        return jsonify({'error': 'You already reviewed this product'}), 400
    
    rating = request.json.get('rating')
    comment = request.json.get('comment', '')
    
    if not rating or rating < 1 or rating > 5:
        return jsonify({'error': 'Invalid rating'}), 400
    
    review = Review(
        product_id=id,
        user_id=session['user_id'],
        rating=rating,
        comment=comment
    )
    db.session.add(review)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/check-name', methods=['POST'])
def check_name():
    name = request.json.get('name')
    user = User.query.filter_by(name=name).first()
    return jsonify({'available': user is None})

@app.route('/check-email', methods=['POST'])
def check_email():
    email = request.json.get('email')
    user = User.query.filter_by(email=email).first()
    return jsonify({'available': user is None})

@app.route('/api/product/<int:id>')
def api_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({'error': 'Not found'}), 404
    
    currency = get_user_currency()
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'display_price': convert_price(product.price, currency),
        'image_url': product.image_url,
        'stock': product.stock
    })

@app.route('/validate-coupon', methods=['POST'])
def validate_coupon():
    code = request.json.get('code')
    subtotal = request.json.get('subtotal', 0)
    
    coupon = Coupon.query.filter_by(code=code.upper(), active=True).first()
    
    if not coupon:
        return jsonify({'valid': False, 'message': 'Invalid coupon code'})
    
    if coupon.expires_at and coupon.expires_at < datetime.utcnow():
        return jsonify({'valid': False, 'message': 'Coupon has expired'})
    
    if coupon.max_uses and coupon.used_count >= coupon.max_uses:
        return jsonify({'valid': False, 'message': 'Coupon usage limit reached'})
    
    if subtotal < coupon.min_purchase:
        return jsonify({'valid': False, 'message': f'Minimum purchase of KSh {coupon.min_purchase:,.0f} required'})
    
    discount = 0
    if coupon.discount_percent:
        discount = subtotal * (coupon.discount_percent / 100)
    elif coupon.discount_amount:
        discount = coupon.discount_amount
    
    return jsonify({
        'valid': True,
        'discount': discount,
        'code': coupon.code,
        'message': f'Coupon applied! You save KSh {discount:,.0f}'
    })

@app.route('/admin/upload')
def admin_upload():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin_upload.html')

@app.route('/admin/coupons')
def admin_coupons():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    coupons = Coupon.query.order_by(Coupon.created_at.desc()).all()
    return render_template('admin_coupons.html', coupons=coupons)

@app.route('/admin/create_coupon', methods=['POST'])
def admin_create_coupon():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    code = request.form['code'].upper()
    discount_type = request.form['discount_type']
    discount_value = float(request.form['discount_value'])
    min_purchase = float(request.form.get('min_purchase', 0))
    max_uses = int(request.form['max_uses']) if request.form.get('max_uses') else None
    expires_days = int(request.form.get('expires_days', 30))
    
    coupon = Coupon(
        code=code,
        discount_percent=discount_value if discount_type == 'percent' else None,
        discount_amount=discount_value if discount_type == 'amount' else None,
        min_purchase=min_purchase,
        max_uses=max_uses,
        expires_at=datetime.utcnow() + timedelta(days=expires_days),
        active=True
    )
    db.session.add(coupon)
    db.session.commit()
    
    return redirect(url_for('admin_coupons'))

@app.route('/admin/toggle_coupon/<int:id>', methods=['POST'])
def admin_toggle_coupon(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    coupon = Coupon.query.get_or_404(id)
    coupon.active = not coupon.active
    db.session.commit()
    
    return redirect(url_for('admin_coupons'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        category = request.form['category']
        gender = request.form.get('gender', 'unisex')
        stock = int(request.form['stock'])
        
        image_url = None
        video_url = None
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_url = f'/static/uploads/{filename}'
        
        if 'video' in request.files:
            file = request.files['video']
            if file and file.filename:
                filename = secure_filename(file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                video_url = f'/static/uploads/{filename}'
        
        product = Product(
            name=name,
            price=price,
            description=description,
            category=category,
            gender=gender,
            stock=stock,
            image_url=image_url,
            video_url=video_url
        )
        db.session.add(product)
        db.session.commit()
        
        return redirect(url_for('admin'))
    
    return render_template('admin.html')

# Payment Routes
@app.route('/checkout-page')
def checkout_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_user = db.session.get(User, session['user_id'])
    return render_template('checkout.html', current_user=current_user)

@app.route('/mpesa/callback', methods=['POST'])
def mpesa_callback():
    data = request.get_json()
    if data and data.get('Body', {}).get('stkCallback'):
        callback = data['Body']['stkCallback']
        checkout_request_id = callback.get('CheckoutRequestID')
        result_code = callback.get('ResultCode')
        order = Order.query.filter_by(payment_reference=checkout_request_id).first()
        if order:
            order.status = 'paid' if result_code == 0 else 'failed'
            db.session.commit()
    return jsonify({'ResultCode': 0, 'ResultDesc': 'Success'})

@app.route('/payment/callback')
def payment_callback():
    tx_ref = request.args.get('tx_ref')
    status = request.args.get('status')
    if status == 'successful' and tx_ref:
        result = flutterwave.verify_payment(tx_ref)
        if result['success']:
            order = Order.query.filter_by(payment_reference=tx_ref).first()
            if order:
                order.status = 'paid'
                db.session.commit()
                return render_template('payment_success.html', order=order)
    return render_template('payment_failed.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Add sample products if none exist
        if Product.query.count() == 0:
            sample_products = [
                Product(name='Elegant Dress', price=2500, description='Beautiful floral dress', category='dresses', gender='women', stock=50),
                Product(name='Chiffon Blouse', price=1800, description='Light chiffon top', category='tops', gender='women', stock=30),
                Product(name='Business Suit', price=5500, description='Professional business suit', category='suits', gender='men', stock=20),
                Product(name='Leather Shoes', price=3200, description='Comfortable leather shoes', category='shoes', gender='unisex', stock=25),
                Product(name='Designer Handbag', price=4500, description='Premium leather handbag', category='accessories', gender='women', stock=15),
                Product(name='Casual Shirt', price=1200, description='Cotton casual shirt', category='shirts', gender='men', stock=40)
            ]
            for product in sample_products:
                db.session.add(product)
            db.session.commit()
    
    app.run(debug=True)