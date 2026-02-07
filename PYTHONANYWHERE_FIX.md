# PythonAnywhere Deployment Fix Guide

## 🚨 Current Issues
1. Missing database columns (`flash_sale_price`, `flash_sale_end`, `coupon_code`, `discount_amount`)
2. Missing environment variables (`ADMIN_USER`, `ADMIN_PASS`)
3. Database file access issues

## 🔧 Step-by-Step Fix

### Step 1: Set Environment Variables

1. Go to PythonAnywhere Dashboard
2. Click on "Files" tab
3. Navigate to: `/home/emonigatsaucee/wegatsauceefashionhub/`
4. Create a new file named `.env`
5. Add the following content:

```bash
SECRET_KEY=your-secret-key-change-this
SQLALCHEMY_DATABASE_URI=sqlite:////home/emonigatsaucee/wegatsauceefashionhub/instance/wegatsaucee.db
ADMIN_USER=admin
ADMIN_PASS=admin123
```

### Step 2: Run Database Migration

1. Open a **Bash console** in PythonAnywhere
2. Navigate to your project:
```bash
cd ~/wegatsauceefashionhub
```

3. Activate your virtual environment:
```bash
source ~/.virtualenvs/myenv/bin/activate
```

4. Run the migration script:
```bash
python migrate_database.py
```

### Step 3: Fix Database Permissions

```bash
# Ensure instance directory exists
mkdir -p ~/wegatsauceefashionhub/instance

# Set proper permissions
chmod 755 ~/wegatsauceefashionhub/instance
chmod 644 ~/wegatsauceefashionhub/instance/wegatsaucee.db
```

### Step 4: Reload Web App

1. Go to "Web" tab in PythonAnywhere
2. Click the green "Reload" button
3. Test your site

## 🔍 Verification Steps

### Check if migration worked:
```bash
cd ~/wegatsauceefashionhub
source ~/.virtualenvs/myenv/bin/activate
python -c "
from app import app, db, Product, Order
with app.app_context():
    # Check Product table
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    product_cols = [c['name'] for c in inspector.get_columns('product')]
    print('Product columns:', product_cols)
    
    # Check Order table
    order_cols = [c['name'] for c in inspector.get_columns('order')]
    print('Order columns:', order_cols)
"
```

### Check environment variables:
```bash
cd ~/wegatsauceefashionhub
python -c "
from decouple import config
print('ADMIN_USER:', config('ADMIN_USER', default='NOT SET'))
print('ADMIN_PASS:', config('ADMIN_PASS', default='NOT SET'))
"
```

## 🐛 Troubleshooting

### Issue: "unable to open database file"

**Solution:**
```bash
# Check if database exists
ls -la ~/wegatsauceefashionhub/instance/wegatsaucee.db

# If not, create it:
cd ~/wegatsauceefashionhub
source ~/.virtualenvs/myenv/bin/activate
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database created!')
"
```

### Issue: "no such table: product"

**Solution:**
```bash
cd ~/wegatsauceefashionhub
source ~/.virtualenvs/myenv/bin/activate
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('All tables created!')
"
```

### Issue: "ADMIN_USER not found"

**Solution:**
1. Make sure `.env` file exists in project root
2. Check file content:
```bash
cat ~/wegatsauceefashionhub/.env
```
3. If missing, create it with the content from Step 1

## 📝 Alternative: Manual Database Fix

If migration script doesn't work, manually add columns:

```bash
cd ~/wegatsauceefashionhub
sqlite3 instance/wegatsaucee.db

# In SQLite prompt:
ALTER TABLE product ADD COLUMN flash_sale_price REAL;
ALTER TABLE product ADD COLUMN flash_sale_end DATETIME;
ALTER TABLE "order" ADD COLUMN coupon_code VARCHAR(50);
ALTER TABLE "order" ADD COLUMN discount_amount REAL DEFAULT 0;
.quit
```

## ✅ Success Checklist

- [ ] `.env` file created with ADMIN_USER and ADMIN_PASS
- [ ] Database migration completed successfully
- [ ] Database file has proper permissions
- [ ] Web app reloaded
- [ ] Homepage loads without errors
- [ ] Admin login works (admin/admin123)
- [ ] Products page displays correctly

## 🆘 Still Having Issues?

Check error logs:
```bash
# View error log
tail -100 /var/log/emonigatsaucee.pythonanywhere.com.error.log

# View server log
tail -100 /var/log/emonigatsaucee.pythonanywhere.com.server.log
```

## 📞 Quick Commands Reference

```bash
# Navigate to project
cd ~/wegatsauceefashionhub

# Activate virtual environment
source ~/.virtualenvs/myenv/bin/activate

# Run migration
python migrate_database.py

# Check database
sqlite3 instance/wegatsaucee.db ".tables"

# View environment variables
cat .env

# Restart web app (do this in Web tab on PythonAnywhere dashboard)
```

## 🎯 Expected Result

After following these steps:
- ✅ Homepage loads successfully
- ✅ Products display correctly
- ✅ Admin login works
- ✅ No database errors in logs
- ✅ Orders can be created
- ✅ Tracking works
