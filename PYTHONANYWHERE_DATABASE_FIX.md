# 🚨 PYTHONANYWHERE DATABASE FIX

## Error: "unable to open database file"

This error occurs because the database path is incorrect on PythonAnywhere.

## ⚡ QUICK FIX (Run on PythonAnywhere Console)

```bash
cd ~/wegatsauceefashionhub
source ~/.virtualenvs/myenv/bin/activate
python pythonanywhere_fix.py
```

Then **reload your web app** in the PythonAnywhere Web tab.

---

## 📋 MANUAL FIX (If script doesn't work)

### Step 1: Open PythonAnywhere Bash Console

Go to: https://www.pythonanywhere.com/user/emonigatsaucee/consoles/

### Step 2: Navigate to Project

```bash
cd ~/wegatsauceefashionhub
```

### Step 3: Activate Virtual Environment

```bash
source ~/.virtualenvs/myenv/bin/activate
```

### Step 4: Create Instance Directory

```bash
mkdir -p instance
chmod 755 instance
```

### Step 5: Initialize Database

```bash
python3 << 'EOF'
from app import app, db, Product
import os

with app.app_context():
    # Create all tables
    db.create_all()
    print("✓ Database created")
    
    # Add sample products if none exist
    if Product.query.count() == 0:
        products = [
            Product(name='Elegant Dress', price=2500, description='Beautiful floral dress', 
                   category='dresses', gender='women', stock=50, is_trending=True),
            Product(name='Chiffon Blouse', price=1800, description='Light chiffon top', 
                   category='tops', gender='women', stock=30, is_trending=True),
            Product(name='Business Suit', price=5500, description='Professional business suit', 
                   category='suits', gender='men', stock=20, is_trending=True),
            Product(name='Leather Shoes', price=3200, description='Comfortable leather shoes', 
                   category='shoes', gender='unisex', stock=25, is_trending=True),
            Product(name='Designer Handbag', price=4500, description='Premium leather handbag', 
                   category='accessories', gender='women', stock=15, is_trending=True),
            Product(name='Casual Shirt', price=1200, description='Cotton casual shirt', 
                   category='shirts', gender='men', stock=40, is_trending=True)
        ]
        for p in products:
            db.session.add(p)
        db.session.commit()
        print(f"✓ Added {len(products)} products")
    
    print("✅ Setup complete!")
EOF
```

### Step 6: Set Permissions

```bash
chmod 644 instance/wegatsaucee.db
```

### Step 7: Reload Web App

1. Go to: https://www.pythonanywhere.com/user/emonigatsaucee/webapps/
2. Click the **Reload** button
3. Visit your site

---

## 🔍 VERIFY FIX

After reloading, check the error log:
- Go to Web tab
- Click on "Error log" link
- Should see no more "unable to open database file" errors

---

## 🛠️ ALTERNATIVE: Update WSGI File

If the above doesn't work, update your WSGI file:

1. Go to Web tab
2. Click on WSGI configuration file link
3. Make sure it has:

```python
import sys
import os

# Add project directory
project_home = '/home/emonigatsaucee/wegatsauceefashionhub'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set working directory
os.chdir(project_home)

# Import Flask app
from app import app as application
```

4. Save and reload

---

## 📞 STILL NOT WORKING?

### Check Database Path

```bash
cd ~/wegatsauceefashionhub
python3 -c "from app import app; print(app.config['SQLALCHEMY_DATABASE_URI'])"
```

Should output: `sqlite:////home/emonigatsaucee/wegatsauceefashionhub/instance/wegatsaucee.db`

### Check File Exists

```bash
ls -la ~/wegatsauceefashionhub/instance/
```

Should show `wegatsaucee.db` file.

### Check Permissions

```bash
ls -la ~/wegatsauceefashionhub/instance/wegatsaucee.db
```

Should show: `-rw-r--r--` (644 permissions)

---

## 💡 PREVENTION

To prevent this in future:

1. Always use absolute paths on PythonAnywhere
2. Ensure instance directory exists before deployment
3. Set proper file permissions (755 for directories, 644 for files)
4. Test database connection after each deployment

---

## ✅ SUCCESS INDICATORS

Your site is working when:
- ✓ Homepage loads without errors
- ✓ Products are visible
- ✓ No database errors in error log
- ✓ Can register/login users
- ✓ Admin panel accessible

---

**Need more help?** Check the error log for specific error messages.
