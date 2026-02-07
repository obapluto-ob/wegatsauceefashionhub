# 🔧 PythonAnywhere Error Troubleshooting Flowchart

## START HERE: Getting Internal Server Error?

### Step 1: Check Error Log
**Location:** PythonAnywhere Web tab → Log files → Error log

---

## Common Errors & Solutions

### ❌ Error: "No module named 'flask'"
**Cause:** Dependencies not installed
**Fix:**
```bash
cd ~/turktrendyshop
pip3 install --user -r requirements.txt
```
**Then:** Reload web app

---

### ❌ Error: "No module named 'decouple'"
**Cause:** python-decouple not installed
**Fix:**
```bash
pip3 install --user python-decouple
```
**Then:** Reload web app

---

### ❌ Error: "No such file or directory: 'wegatsaucee.db'"
**Cause:** Database not created or wrong path
**Fix:**
```bash
cd ~/turktrendyshop
python3 init_db.py
```
**Then:** Reload web app

---

### ❌ Error: "unable to open database file"
**Cause:** Database file permissions issue
**Fix:**
```bash
chmod 755 ~/turktrendyshop/instance
chmod 666 ~/turktrendyshop/instance/wegatsaucee.db
```
**Then:** Reload web app

---

### ❌ Error: "Permission denied"
**Cause:** File/folder permissions wrong
**Fix:**
```bash
chmod -R 755 ~/turktrendyshop
chmod 666 ~/turktrendyshop/instance/*.db
```
**Then:** Reload web app

---

### ❌ Error: "No module named 'app'"
**Cause:** WSGI file not configured correctly
**Fix:** Edit WSGI file with correct path:
```python
project_home = '/home/YOURUSERNAME/turktrendyshop'  # Fix this!
```
**Then:** Reload web app

---

### ❌ Error: "ImportError: cannot import name 'app'"
**Cause:** Circular import or syntax error in app.py
**Fix:** Test app.py directly:
```bash
cd ~/turktrendyshop
python3 app.py
```
Look for syntax errors, fix them
**Then:** Reload web app

---

### ❌ Error: "Database is locked"
**Cause:** Multiple processes accessing database
**Fix:**
```bash
# Stop any running processes
pkill -f app.py

# Fix permissions
chmod 666 ~/turktrendyshop/instance/wegatsaucee.db

# Restart
```
**Then:** Reload web app

---

### ❌ Error: "No such table: user" or "No such table: product"
**Cause:** Database tables not created
**Fix:**
```bash
cd ~/turktrendyshop
python3 init_db.py
```
**Then:** Reload web app

---

### ❌ Error: "Static files not loading" (CSS/Images missing)
**Cause:** Static files not mapped
**Fix:** In PythonAnywhere Web tab → Static files:
- URL: `/static/`
- Directory: `/home/YOURUSERNAME/turktrendyshop/static/`
**Then:** Reload web app

---

### ❌ Error: "500 Internal Server Error" (No specific error in log)
**Cause:** Multiple possible issues
**Fix:** Run diagnostic:
```bash
cd ~/turktrendyshop
python3 check_deployment.py
```
Fix any issues shown
**Then:** Reload web app

---

## 🔄 Universal Fix (When Nothing Else Works)

### Nuclear Option - Complete Reinstall:

```bash
# 1. Navigate to project
cd ~/turktrendyshop

# 2. Backup database (if exists)
cp instance/wegatsaucee.db instance/backup.db

# 3. Reinstall all dependencies
pip3 install --user --force-reinstall -r requirements.txt

# 4. Fix permissions
chmod -R 755 ~/turktrendyshop
chmod 755 ~/turktrendyshop/instance
chmod 666 ~/turktrendyshop/instance/*.db

# 5. Recreate database
python3 init_db.py

# 6. Test import
python3 -c "from app import app; print('Success!')"
```

**Then:** 
1. Check WSGI configuration
2. Reload web app
3. Test site

---

## 📊 Diagnostic Commands

### Check if app imports correctly:
```bash
python3 -c "from app import app, db; print('OK')"
```

### Check database:
```bash
python3 -c "from app import app, db, Product; app.app_context().push(); print(Product.query.count())"
```

### Check dependencies:
```bash
pip3 list | grep -i flask
pip3 list | grep -i sqlalchemy
pip3 list | grep -i decouple
```

### View recent errors:
```bash
tail -50 /var/log/YOURUSERNAME.pythonanywhere.com.error.log
```

---

## ✅ Verification Steps

After fixing, verify these work:

1. **Homepage:**
   ```
   https://YOURUSERNAME.pythonanywhere.com/
   ```
   Should show products

2. **Admin Panel:**
   ```
   https://YOURUSERNAME.pythonanywhere.com/admin/login
   ```
   Login: admin / admin123

3. **Products Page:**
   ```
   https://YOURUSERNAME.pythonanywhere.com/products
   ```
   Should show product catalog

4. **Registration:**
   ```
   https://YOURUSERNAME.pythonanywhere.com/register
   ```
   Try creating account

---

## 🆘 Still Stuck?

### Gather This Information:

1. **Error Log Output:**
   ```bash
   tail -100 /var/log/YOURUSERNAME.pythonanywhere.com.error.log
   ```

2. **Diagnostic Output:**
   ```bash
   python3 check_deployment.py
   ```

3. **Import Test:**
   ```bash
   python3 -c "from app import app; print('Success')"
   ```

4. **Your PythonAnywhere Username**

Share this information and I'll help you fix it!

---

## 📝 Prevention Checklist

Before deploying, always:
- [ ] Test locally: `python app.py`
- [ ] Check all files uploaded
- [ ] Install dependencies: `pip3 install --user -r requirements.txt`
- [ ] Initialize database: `python3 init_db.py`
- [ ] Configure WSGI with correct username
- [ ] Map static files
- [ ] Check error log after reload
- [ ] Test all main pages

---

## 🎯 Success Indicators

Your deployment is successful when:
- ✅ No errors in error log
- ✅ Homepage loads with products
- ✅ Admin panel accessible
- ✅ Can register new users
- ✅ Can add products to cart
- ✅ Static files (CSS/images) load

---

**Remember:** After EVERY change, click "Reload" in Web tab!

Good luck! 🚀
