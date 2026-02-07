# PythonAnywhere Deployment Guide

## Quick Update Steps

### Method 1: Pull from GitHub (Recommended)

1. **Open PythonAnywhere Console**
   - Go to https://www.pythonanywhere.com
   - Login to your account
   - Click "Consoles" → "Bash"

2. **Navigate to Your Project**
   ```bash
   cd wegatsauceefashionhub
   ```

3. **Pull Latest Changes**
   ```bash
   git pull origin main
   ```

4. **Update Database Schema**
   ```bash
   python3 init_db.py
   ```

5. **Reload Web App**
   - Go to "Web" tab
   - Click green "Reload" button for `emonigatsaucee.pythonanywhere.com`

### Method 2: Manual File Upload

1. **Go to Files Tab**
   - Navigate to `/home/emonigatsaucee/wegatsauceefashionhub/`

2. **Upload Changed Files**
   - Upload `app.py`
   - Upload `templates/` folder files
   - Upload any new files

3. **Update Database**
   - Open Bash console
   - Run: `cd wegatsauceefashionhub && python3 init_db.py`

4. **Reload Web App**
   - Go to "Web" tab → Click "Reload"

## What's New in This Update

### Phase 1 Features ✅
- **Product Videos Display** - Videos play on product pages
- **Size/Color Selection** - Interactive size/color picker
- **Low Stock Warning** - Alerts when stock < 10

### Phase 2 Features ✅
- **Related Products** - "You May Also Like" section
- **Flash Sales** - Time-limited discounts (database ready)
- **Coupon Codes** - Discount code system with validation

## Database Changes

New tables/columns added:
- `Product.flash_sale_price` - Flash sale price
- `Product.flash_sale_end` - Flash sale end time
- `Order.coupon_code` - Applied coupon code
- `Order.discount_amount` - Discount amount
- `Coupon` table - Coupon management

## Testing After Deployment

1. **Test Product Videos**
   - Visit any product with videos
   - Click video thumbnail to play

2. **Test Size/Color Selection**
   - Select size and color
   - Add to cart
   - Verify in cart

3. **Test Coupon Codes**
   - Go to checkout
   - Enter coupon code
   - Verify discount applied

4. **Test Related Products**
   - View any product
   - Scroll down to see "You May Also Like"

## Troubleshooting

### If site shows errors:

1. **Check Error Log**
   - Web tab → Error log link
   - Look for Python errors

2. **Verify Database**
   ```bash
   cd wegatsauceefashionhub
   python3
   >>> from app import db, app
   >>> with app.app_context():
   ...     db.create_all()
   >>> exit()
   ```

3. **Check File Permissions**
   ```bash
   chmod 644 *.py
   chmod 755 static/
   ```

4. **Reload Again**
   - Sometimes needs 2-3 reloads

## Admin Features

### Create Coupon Codes (via Python console)

```python
from app import app, db, Coupon
from datetime import datetime, timedelta

with app.app_context():
    # 10% off coupon
    coupon = Coupon(
        code='SAVE10',
        discount_percent=10,
        min_purchase=1000,
        max_uses=100,
        expires_at=datetime.utcnow() + timedelta(days=30),
        active=True
    )
    db.session.add(coupon)
    db.session.commit()
    print("Coupon created!")
```

### Set Flash Sale (via Python console)

```python
from app import app, db, Product
from datetime import datetime, timedelta

with app.app_context():
    product = Product.query.get(1)  # Product ID
    product.flash_sale_price = 1500  # Sale price
    product.flash_sale_end = datetime.utcnow() + timedelta(hours=24)
    db.session.commit()
    print("Flash sale set!")
```

## Support

- GitHub: https://github.com/obapluto-ob/wegatsauceefashionhub
- Live Site: https://emonigatsaucee.pythonanywhere.com
