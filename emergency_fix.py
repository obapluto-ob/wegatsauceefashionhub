#!/usr/bin/env python3
"""
EMERGENCY FIX for PythonAnywhere Database Errors
Run this on PythonAnywhere to fix all current issues
"""

import sqlite3
import os

print("=" * 70)
print("  EMERGENCY DATABASE FIX")
print("=" * 70)

# Step 1: Find database
db_paths = ['ecommerce.db', 'instance/ecommerce.db', 'instance/wegatsaucee.db']
db_path = None

for path in db_paths:
    if os.path.exists(path):
        db_path = path
        break

if not db_path:
    print("\n❌ ERROR: No database found!")
    print("Creating new database at: ecommerce.db")
    db_path = 'ecommerce.db'

print(f"\n✓ Using database: {db_path}")

# Step 2: Connect and fix
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "-" * 70)
    print("FIXING PRODUCT TABLE")
    print("-" * 70)
    
    # Get current columns
    cursor.execute("PRAGMA table_info(product)")
    columns = {col[1] for col in cursor.fetchall()}
    
    # Add missing columns
    fixes = [
        ('flash_sale_price', 'REAL', 'Flash sale price'),
        ('flash_sale_end', 'DATETIME', 'Flash sale end date')
    ]
    
    for col_name, col_type, description in fixes:
        if col_name not in columns:
            try:
                cursor.execute(f"ALTER TABLE product ADD COLUMN {col_name} {col_type}")
                print(f"✓ Added: {description}")
            except Exception as e:
                print(f"✗ Failed to add {col_name}: {e}")
        else:
            print(f"✓ Already exists: {description}")
    
    print("\n" + "-" * 70)
    print("FIXING ORDER TABLE")
    print("-" * 70)
    
    # Get current columns
    cursor.execute("PRAGMA table_info('order')")
    columns = {col[1] for col in cursor.fetchall()}
    
    # Add missing columns
    fixes = [
        ('coupon_code', 'VARCHAR(50)', 'Coupon code'),
        ('discount_amount', 'REAL DEFAULT 0', 'Discount amount')
    ]
    
    for col_name, col_type, description in fixes:
        if col_name not in columns:
            try:
                cursor.execute(f"ALTER TABLE 'order' ADD COLUMN {col_name} {col_type}")
                print(f"✓ Added: {description}")
            except Exception as e:
                print(f"✗ Failed to add {col_name}: {e}")
        else:
            print(f"✓ Already exists: {description}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 70)
    print("  ✓ DATABASE FIXED SUCCESSFULLY!")
    print("=" * 70)
    print("\nNEXT STEPS:")
    print("1. Create .env file with:")
    print("   ADMIN_USER=admin")
    print("   ADMIN_PASS=admin123")
    print("   SECRET_KEY=your-secret-key")
    print("\n2. Fix permissions:")
    print(f"   chmod 664 {db_path}")
    print("\n3. Reload your web app in PythonAnywhere")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nTry running: python quick_fix.py")
