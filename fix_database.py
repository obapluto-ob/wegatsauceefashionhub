#!/usr/bin/env python3
"""
Database Migration Script for PythonAnywhere
Fixes missing columns and schema issues
"""

import sqlite3
import os
import sys

def fix_database():
    # Get the database path
    db_path = os.path.join(os.path.dirname(__file__), 'ecommerce.db')
    
    print(f"Fixing database at: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"ERROR: Database file not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check and add missing columns to Product table
        print("\n1. Checking Product table...")
        cursor.execute("PRAGMA table_info(product)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'flash_sale_price' not in columns:
            print("   Adding flash_sale_price column...")
            cursor.execute("ALTER TABLE product ADD COLUMN flash_sale_price REAL")
        
        if 'flash_sale_end' not in columns:
            print("   Adding flash_sale_end column...")
            cursor.execute("ALTER TABLE product ADD COLUMN flash_sale_end DATETIME")
        
        # Check and add missing columns to Order table
        print("\n2. Checking Order table...")
        cursor.execute("PRAGMA table_info('order')")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'coupon_code' not in columns:
            print("   Adding coupon_code column...")
            cursor.execute("ALTER TABLE 'order' ADD COLUMN coupon_code VARCHAR(50)")
        
        if 'discount_amount' not in columns:
            print("   Adding discount_amount column...")
            cursor.execute("ALTER TABLE 'order' ADD COLUMN discount_amount REAL DEFAULT 0")
        
        conn.commit()
        print("\n✓ Database migration completed successfully!")
        
        # Verify changes
        print("\n3. Verifying Product table columns:")
        cursor.execute("PRAGMA table_info(product)")
        for col in cursor.fetchall():
            print(f"   - {col[1]} ({col[2]})")
        
        print("\n4. Verifying Order table columns:")
        cursor.execute("PRAGMA table_info('order')")
        for col in cursor.fetchall():
            print(f"   - {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE MIGRATION SCRIPT")
    print("=" * 60)
    
    success = fix_database()
    
    if success:
        print("\n" + "=" * 60)
        print("MIGRATION SUCCESSFUL!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Reload your web app in PythonAnywhere")
        print("2. Test the homepage and admin panel")
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("MIGRATION FAILED!")
        print("=" * 60)
        sys.exit(1)
