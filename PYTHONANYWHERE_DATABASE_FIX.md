# PythonAnywhere Database Fix Guide

## Current Issues
Your PythonAnywhere deployment has these errors:
1. ❌ Missing database columns (flash_sale_price, coupon_code, etc.)
2. ❌ Unable to open database file
3. ❌ Missing environment variables

## Quick Fix (Run on PythonAnywhere)

### Step 1: Open Bash Console
Go to PythonAnywhere → Consoles → Start a new Bash console

### Step 2: Navigate to Your Project
```bash
cd ~/wegatsauceefashionhub
```

### Step 3: Activate Virtual Environment
```bash
source ~/.virtualenvs/myenv/bin/activate
```

### Step 4: Create .env File
```bash
cat > .env << 'EOF'
SECRET_KEY=your-secret-key-change-this
ADMIN_USER=admin
ADMIN_PASS=admin123
DATABASE_URL=sqlite:///ecommerce.db
EOF
```

### Step 5: Run Database Migration
```bash
python fix_database.py
```

### Step 6: Fix Database Permissions
```bash
chmod 664 ecommerce.db
chmod 775 .
```

### Step 7: Reload Web App
Go to PythonAnywhere → Web → Click "Reload" button

## Alternative: Complete Reset

If the above doesn't work, do a complete database reset:

```bash
cd ~/wegatsauceefashionhub
source ~/.virtualenvs/myenv/bin/activate

# Backup old database
mv ecommerce.db ecommerce.db.backup

# Create fresh database
python << 'EOF'
from app import app, db
with app.app_context():
    db.create_all()
    print("Database created successfully!")
EOF

# Run the quick fix script
python quick_fix.py
```

## Verify It's Working

1. Visit your site homepage
2. Try logging in as admin (admin/admin123)
3. Check if products load correctly

## Common Issues & Solutions

### Issue: "unable to open database file"
**Solution:**
```bash
cd ~/wegatsauceefashionhub
chmod 664 ecommerce.db
chmod 775 .
```

### Issue: "ADMIN_USER not found"
**Solution:**
```bash
cd ~/wegatsauceefashionhub
echo "ADMIN_USER=admin" >> .env
echo "ADMIN_PASS=admin123" >> .env
```

### Issue: "no such column"
**Solution:**
```bash
cd ~/wegatsauceefashionhub
python fix_database.py
```

## Need More Help?

If you're still having issues:
1. Check error logs: PythonAnywhere → Web → Error log
2. Verify file permissions: `ls -la ~/wegatsauceefashionhub/`
3. Check database exists: `ls -la ~/wegatsauceefashionhub/*.db`

## Contact
For urgent issues, check the PythonAnywhere forums or contact support.
