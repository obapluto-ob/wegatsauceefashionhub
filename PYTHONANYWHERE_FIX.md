# PythonAnywhere Deployment Fix Guide

## Common Internal Server Error Causes & Solutions

### 1. Database Path Issue (MOST COMMON)
**Problem:** SQLite database path not found
**Solution:** Database is now in `instance/` folder

### 2. Missing Dependencies
**Problem:** Import errors for custom modules
**Solution:** All dependencies are in requirements.txt

### 3. File Permissions
**Problem:** Can't write to database or upload files
**Solution:** Check folder permissions on PythonAnywhere

---

## Step-by-Step Deployment to PythonAnywhere

### Step 1: Upload Your Files
1. Go to PythonAnywhere Dashboard
2. Click on "Files" tab
3. Upload all files to `/home/yourusername/turktrendyshop/`
4. Make sure these folders exist:
   - `instance/` (for database)
   - `static/uploads/` (for images)
   - `templates/` (for HTML files)
   - `logs/` (for log files)

### Step 2: Install Dependencies
1. Open a Bash console on PythonAnywhere
2. Navigate to your project:
   ```bash
   cd ~/turktrendyshop
   ```
3. Install requirements:
   ```bash
   pip3 install --user -r requirements.txt
   ```

### Step 3: Initialize Database
1. In the same Bash console:
   ```bash
   python3 init_db.py
   ```
   OR manually:
   ```bash
   python3
   >>> from app import app, db
   >>> with app.app_context():
   ...     db.create_all()
   >>> exit()
   ```

### Step 4: Configure WSGI File
1. Go to "Web" tab on PythonAnywhere
2. Click on your web app
3. Scroll to "Code" section
4. Click on WSGI configuration file link
5. Replace ALL content with:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOURUSERNAME/turktrendyshop'  # CHANGE YOURUSERNAME
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment to production
os.environ['FLASK_ENV'] = 'production'

# Import Flask app
from app import app as application
```

**IMPORTANT:** Replace `YOURUSERNAME` with your actual PythonAnywhere username!

### Step 5: Set Static Files
1. Still in "Web" tab
2. Scroll to "Static files" section
3. Add these mappings:

| URL | Directory |
|-----|-----------|
| /static/ | /home/YOURUSERNAME/turktrendyshop/static/ |

### Step 6: Check Error Logs
1. In "Web" tab, scroll to "Log files"
2. Click on "Error log" to see what's wrong
3. Common errors and fixes:

#### Error: "No module named 'decouple'"
**Fix:** Run `pip3 install --user python-decouple`

#### Error: "No such file or directory: 'wegatsaucee.db'"
**Fix:** Database path issue - already fixed in code above

#### Error: "Permission denied"
**Fix:** Run in Bash console:
```bash
chmod 755 ~/turktrendyshop
chmod 755 ~/turktrendyshop/instance
chmod 666 ~/turktrendyshop/instance/wegatsaucee.db
```

#### Error: "Import error: payments, logger, security"
**Fix:** Make sure all .py files are uploaded:
- payments.py
- logger.py
- security.py
- email_notifications.py (if exists)

### Step 7: Reload Web App
1. Go back to "Web" tab
2. Click the big green "Reload" button
3. Visit your site: `https://yourusername.pythonanywhere.com`

---

## Quick Troubleshooting Checklist

- [ ] All files uploaded to PythonAnywhere
- [ ] `instance/` folder exists
- [ ] `static/uploads/` folder exists
- [ ] Dependencies installed: `pip3 install --user -r requirements.txt`
- [ ] Database initialized: `python3 init_db.py`
- [ ] WSGI file configured with correct username
- [ ] Static files mapped correctly
- [ ] Web app reloaded
- [ ] Error log checked

---

## Testing Your Deployment

1. **Homepage:** Visit `https://yourusername.pythonanywhere.com/`
   - Should show product catalog

2. **Admin Panel:** Visit `https://yourusername.pythonanywhere.com/admin/login`
   - Login: admin / admin123

3. **Registration:** Try creating a new account

4. **Check Logs:** If errors occur, check:
   - Error log in PythonAnywhere Web tab
   - `logs/` folder in your project

---

## Environment Variables on PythonAnywhere

If you need to use environment variables:

1. Go to "Web" tab
2. Scroll to "Virtualenv" section (optional)
3. Or add to WSGI file:
```python
os.environ['SECRET_KEY'] = 'your-secret-key'
os.environ['ADMIN_USER'] = 'admin'
os.environ['ADMIN_PASS'] = 'admin123'
```

---

## Database Backup on PythonAnywhere

To backup your database:
```bash
cd ~/turktrendyshop/instance
cp wegatsaucee.db wegatsaucee_backup_$(date +%Y%m%d).db
```

---

## Common PythonAnywhere Limitations

1. **Free Account:**
   - Only 1 web app
   - Limited CPU time
   - No HTTPS for custom domains
   - Files expire after 3 months of inactivity

2. **File Upload Size:**
   - Max 100MB per file on free account
   - Adjust in app.py if needed

3. **Database:**
   - SQLite works fine for small sites
   - For larger sites, upgrade to MySQL

---

## Still Getting Errors?

1. **Check Error Log:**
   ```
   Web tab → Log files → Error log
   ```

2. **Check Server Log:**
   ```
   Web tab → Log files → Server log
   ```

3. **Run in Console:**
   ```bash
   cd ~/turktrendyshop
   python3 app.py
   ```
   See what error appears

4. **Common Fix - Reinstall Everything:**
   ```bash
   cd ~/turktrendyshop
   pip3 install --user --force-reinstall -r requirements.txt
   python3 init_db.py
   ```

---

## Contact Support

If you're still stuck:
1. Copy the error from Error Log
2. Share it with me
3. I'll help you fix it!

**Your site should now be working at:**
`https://yourusername.pythonanywhere.com`

Good luck! 🚀
