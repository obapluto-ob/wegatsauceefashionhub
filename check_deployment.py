#!/usr/bin/env python3
"""
Deployment Health Check Script
Run this to diagnose issues: python3 check_deployment.py
"""

import os
import sys

print("=" * 60)
print("PYTHONANYWHERE DEPLOYMENT HEALTH CHECK")
print("=" * 60)

# Check 1: Python version
print("\n1. Python Version:")
print(f"   {sys.version}")
if sys.version_info < (3, 6):
    print("   ⚠ WARNING: Python 3.6+ recommended")
else:
    print("   ✓ OK")

# Check 2: Required folders
print("\n2. Required Folders:")
folders = ['instance', 'static', 'static/uploads', 'templates', 'logs']
for folder in folders:
    if os.path.exists(folder):
        print(f"   ✓ {folder}/")
    else:
        print(f"   ✗ {folder}/ - MISSING!")
        try:
            os.makedirs(folder, exist_ok=True)
            print(f"     → Created {folder}/")
        except:
            print(f"     → Failed to create {folder}/")

# Check 3: Required files
print("\n3. Required Files:")
files = ['app.py', 'requirements.txt', '.env', 'payments.py', 'logger.py', 'security.py']
for file in files:
    if os.path.exists(file):
        print(f"   ✓ {file}")
    else:
        print(f"   ✗ {file} - MISSING!")

# Check 4: Dependencies
print("\n4. Python Dependencies:")
required_packages = [
    'flask',
    'flask_sqlalchemy',
    'werkzeug',
    'requests',
    'decouple'
]

for package in required_packages:
    try:
        __import__(package)
        print(f"   ✓ {package}")
    except ImportError:
        print(f"   ✗ {package} - NOT INSTALLED!")
        print(f"     → Run: pip3 install --user {package}")

# Check 5: Database
print("\n5. Database:")
db_paths = [
    'instance/wegatsaucee.db',
    'wegatsaucee.db',
    'instance/turktrendy.db'
]
db_found = False
for db_path in db_paths:
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"   ✓ {db_path} ({size} bytes)")
        db_found = True
        
        # Check permissions
        if os.access(db_path, os.R_OK):
            print(f"     → Readable: Yes")
        else:
            print(f"     → Readable: No - FIX PERMISSIONS!")
            
        if os.access(db_path, os.W_OK):
            print(f"     → Writable: Yes")
        else:
            print(f"     → Writable: No - FIX PERMISSIONS!")

if not db_found:
    print("   ✗ No database found!")
    print("     → Run: python3 init_db.py")

# Check 6: Environment variables
print("\n6. Environment Variables (.env):")
if os.path.exists('.env'):
    print("   ✓ .env file exists")
    with open('.env', 'r') as f:
        lines = f.readlines()
        for line in lines:
            if '=' in line and not line.startswith('#'):
                key = line.split('=')[0].strip()
                print(f"     → {key}")
else:
    print("   ✗ .env file missing!")

# Check 7: Try importing app
print("\n7. App Import Test:")
try:
    from app import app, db
    print("   ✓ Successfully imported app")
    print(f"   → Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    print(f"   → Secret Key: {'Set' if app.config.get('SECRET_KEY') else 'NOT SET'}")
except Exception as e:
    print(f"   ✗ Failed to import app: {e}")
    import traceback
    traceback.print_exc()

# Check 8: File permissions
print("\n8. File Permissions:")
try:
    test_file = 'instance/test_write.txt'
    with open(test_file, 'w') as f:
        f.write('test')
    os.remove(test_file)
    print("   ✓ Can write to instance/ folder")
except Exception as e:
    print(f"   ✗ Cannot write to instance/ folder: {e}")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("\nIf all checks passed (✓), your deployment should work!")
print("\nIf you see errors (✗), fix them and run this script again.")
print("\nNext steps:")
print("  1. Fix any errors shown above")
print("  2. Run: python3 init_db.py")
print("  3. Configure WSGI file on PythonAnywhere")
print("  4. Reload your web app")
print("\nFor detailed help, see: PYTHONANYWHERE_FIX.md")
print("=" * 60)
