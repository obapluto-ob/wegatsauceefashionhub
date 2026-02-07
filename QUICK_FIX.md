# PythonAnywhere Quick Fix Commands

## 🚨 EMERGENCY FIX - Run These in Order

### 1. Navigate to Project
```bash
cd ~/turktrendyshop
```

### 2. Install Dependencies
```bash
pip3 install --user -r requirements.txt
```

### 3. Check Deployment Health
```bash
python3 check_deployment.py
```

### 4. Initialize Database
```bash
python3 init_db.py
```

### 5. Fix Permissions (if needed)
```bash
chmod 755 ~/turktrendyshop
chmod 755 ~/turktrendyshop/instance
chmod 755 ~/turktrendyshop/static
chmod 755 ~/turktrendyshop/static/uploads
chmod 666 ~/turktrendyshop/instance/*.db
```

### 6. Reload Web App
Go to Web tab → Click "Reload" button

---

## 📝 WSGI Configuration

Replace ENTIRE content of WSGI file with:

```python
import sys
import os

# CHANGE THIS to your username!
project_home = '/home/YOURUSERNAME/turktrendyshop'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['FLASK_ENV'] = 'production'

from app import app as application
```

---

## 🔍 Check Error Logs

### View Error Log
```bash
tail -50 /var/log/YOURUSERNAME.pythonanywhere.com.error.log
```

### View Server Log
```bash
tail -50 /var/log/YOURUSERNAME.pythonanywhere.com.server.log
```

### View App Logs
```bash
tail -50 ~/turktrendyshop/logs/app_*.log
```

---

## 🗄️ Database Commands

### Create Database
```bash
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Check Database
```bash
python3 -c "from app import app, db, Product; app.app_context().push(); print(f'Products: {Product.query.count()}')"
```

### Backup Database
```bash
cp instance/wegatsaucee.db instance/backup_$(date +%Y%m%d_%H%M%S).db
```

---

## 🔧 Common Fixes

### Fix: "No module named 'decouple'"
```bash
pip3 install --user python-decouple
```

### Fix: "No module named 'flask'"
```bash
pip3 install --user Flask Flask-SQLAlchemy
```

### Fix: "Database is locked"
```bash
chmod 666 instance/wegatsaucee.db
```

### Fix: "Permission denied"
```bash
chmod -R 755 ~/turktrendyshop
chmod 666 ~/turktrendyshop/instance/*.db
```

### Fix: "Import error"
```bash
cd ~/turktrendyshop
pip3 install --user --force-reinstall -r requirements.txt
```

---

## 🌐 Static Files Mapping

In Web tab → Static files section:

| URL | Directory |
|-----|-----------|
| /static/ | /home/YOURUSERNAME/turktrendyshop/static/ |

---

## ✅ Verification Checklist

After deployment, test these URLs:

- [ ] Homepage: `https://YOURUSERNAME.pythonanywhere.com/`
- [ ] Products: `https://YOURUSERNAME.pythonanywhere.com/products`
- [ ] Admin: `https://YOURUSERNAME.pythonanywhere.com/admin/login`
- [ ] Register: `https://YOURUSERNAME.pythonanywhere.com/register`

Admin credentials: `admin` / `admin123`

---

## 🆘 Still Not Working?

1. Run health check:
   ```bash
   python3 check_deployment.py
   ```

2. Check error log in PythonAnywhere Web tab

3. Try running app directly:
   ```bash
   python3 app.py
   ```
   (Press Ctrl+C to stop)

4. Reinstall everything:
   ```bash
   pip3 install --user --force-reinstall -r requirements.txt
   python3 init_db.py
   ```

5. Reload web app in Web tab

---

## 📞 Get Help

If still stuck, share:
1. Error message from error log
2. Output of `python3 check_deployment.py`
3. Your PythonAnywhere username

---

**Remember:** After ANY change, always click "Reload" in Web tab!
