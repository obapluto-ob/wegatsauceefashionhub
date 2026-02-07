# 🚨 EMERGENCY FIX - Run These Commands on PythonAnywhere

## Your Current Errors:
- ❌ `no such column: product.flash_sale_price`
- ❌ `no such column: order.coupon_code`
- ❌ `unable to open database file`
- ❌ `ADMIN_USER not found`

## Fix in 5 Minutes:

### 1. Open Bash Console on PythonAnywhere

### 2. Run These Commands (Copy & Paste):

```bash
# Navigate to your project
cd ~/wegatsauceefashionhub

# Activate virtual environment
source ~/.virtualenvs/myenv/bin/activate

# Create .env file
cat > .env << 'EOF'
SECRET_KEY=wegatsaucee-secret-2024
ADMIN_USER=admin
ADMIN_PASS=admin123
EOF

# Run emergency fix
python emergency_fix.py

# Fix permissions
chmod 664 ecommerce.db 2>/dev/null || chmod 664 instance/ecommerce.db 2>/dev/null || chmod 664 instance/wegatsaucee.db
chmod 775 .
chmod 775 instance 2>/dev/null || true
```

### 3. Reload Web App
- Go to PythonAnywhere → Web tab
- Click the green "Reload" button

### 4. Test Your Site
- Visit your homepage
- Try admin login: http://your-site.pythonanywhere.com/admin/login
  - Username: `admin`
  - Password: `admin123`

## Still Not Working?

### Option A: Complete Database Reset
```bash
cd ~/wegatsauceefashionhub
source ~/.virtualenvs/myenv/bin/activate

# Backup old database
mv ecommerce.db ecommerce.db.old 2>/dev/null || true

# Create fresh database
python quick_fix.py

# Reload web app
```

### Option B: Check Logs
```bash
# View error log
tail -50 /var/log/emonigatsaucee.pythonanywhere.com.error.log

# View server log
tail -50 /var/log/emonigatsaucee.pythonanywhere.com.server.log
```

## Files Included:
- `emergency_fix.py` - Quick database column fix
- `fix_database.py` - Detailed migration script
- `quick_fix.py` - Complete setup script
- `.env.example` - Environment variables template

## Need Help?
Check `PYTHONANYWHERE_DATABASE_FIX.md` for detailed troubleshooting.
