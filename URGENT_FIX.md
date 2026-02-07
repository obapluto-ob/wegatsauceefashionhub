# 🚨 URGENT: PythonAnywhere Deployment Fix

## Current Issues
Your PythonAnywhere deployment has 3 main issues:
1. ❌ Missing database columns
2. ❌ Missing environment variables  
3. ❌ Database access permissions

## ⚡ Quick Fix (5 minutes)

### Option 1: Automated Fix (Recommended)

1. **Upload `quick_fix.py` to PythonAnywhere**
   - Go to Files tab
   - Navigate to `/home/emonigatsaucee/wegatsauceefashionhub/`
   - Upload the `quick_fix.py` file

2. **Run the fix script**
   - Open a Bash console
   - Run these commands:
   ```bash
   cd ~/wegatsauceefashionhub
   source ~/.virtualenvs/myenv/bin/activate
   python quick_fix.py
   ```

3. **Reload your web app**
   - Go to Web tab
   - Click the green "Reload" button

4. **Test your site**
   - Visit: https://emonigatsaucee.pythonanywhere.com
   - Admin login: https://emonigatsaucee.pythonanywhere.com/admin/login
   - Username: `admin`
   - Password: `admin123`

### Option 2: Manual Fix

If automated fix doesn't work, follow these steps:

#### Step 1: Create .env file

1. Go to Files tab in PythonAnywhere
2. Navigate to `/home/emonigatsaucee/wegatsauceefashionhub/`
3. Create new file named `.env`
4. Add this content:

```bash
SECRET_KEY=wegatsaucee-secret-key-2024
SQLALCHEMY_DATABASE_URI=sqlite:////home/emonigatsaucee/wegatsauceefashionhub/instance/wegatsaucee.db
ADMIN_USER=admin
ADMIN_PASS=admin123
```

#### Step 2: Fix Database

Open Bash console and run:

```bash
cd ~/wegatsauceefashionhub
source ~/.virtualenvs/myenv/bin/activate

# Run migration
python migrate_database.py

# Or manually fix database:
sqlite3 instance/wegatsaucee.db << EOF
ALTER TABLE product ADD COLUMN flash_sale_price REAL;
ALTER TABLE product ADD COLUMN flash_sale_end DATETIME;
ALTER TABLE "order" ADD COLUMN coupon_code VARCHAR(50);
ALTER TABLE "order" ADD COLUMN discount_amount REAL DEFAULT 0;
.quit
EOF
```

#### Step 3: Fix Permissions

```bash
chmod 755 ~/wegatsauceefashionhub/instance
chmod 644 ~/wegatsauceefashionhub/instance/wegatsaucee.db
```

#### Step 4: Reload Web App

Go to Web tab and click "Reload"

## ✅ Verification

After fixing, verify everything works:

```bash
cd ~/wegatsauceefashionhub
source ~/.virtualenvs/myenv/bin/activate

# Check environment variables
python -c "from decouple import config; print('ADMIN_USER:', config('ADMIN_USER', default='NOT SET'))"

# Check database columns
python -c "
from app import app, db
from sqlalchemy import inspect
with app.app_context():
    inspector = inspect(db.engine)
    print('Product columns:', [c['name'] for c in inspector.get_columns('product')])
    print('Order columns:', [c['name'] for c in inspector.get_columns('order')])
"
```

## 🐛 Troubleshooting

### Error: "unable to open database file"

**Solution:**
```bash
cd ~/wegatsauceefashionhub
mkdir -p instance
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Error: "ADMIN_USER not found"

**Solution:** Make sure `.env` file exists and contains `ADMIN_USER=admin`

### Error: "no such column"

**Solution:** Run the migration script again:
```bash
python migrate_database.py
```

## 📞 Support

If issues persist:
1. Check error logs: `/var/log/emonigatsaucee.pythonanywhere.com.error.log`
2. Check server logs: `/var/log/emonigatsaucee.pythonanywhere.com.server.log`
3. View logs in Bash console:
   ```bash
   tail -50 /var/log/emonigatsaucee.pythonanywhere.com.error.log
   ```

## 🎯 Expected Result

After successful fix:
- ✅ Homepage loads without errors
- ✅ Products display correctly
- ✅ Admin login works (admin/admin123)
- ✅ Orders can be created
- ✅ No database errors in logs

## 📝 Files Included

- `quick_fix.py` - Automated fix script (run this first!)
- `migrate_database.py` - Database migration script
- `.env.example` - Environment variables template
- `PYTHONANYWHERE_FIX.md` - Detailed fix guide

## ⏱️ Estimated Time

- Automated fix: **5 minutes**
- Manual fix: **10-15 minutes**

---

**Need help?** The error logs show exactly what's wrong. Follow the steps above and your site will be working in minutes! 🚀
