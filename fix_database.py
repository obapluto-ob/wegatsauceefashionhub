#!/usr/bin/env python3
"""
Database migration script to add missing tables and columns
Run this on PythonAnywhere to fix database errors
"""

import sqlite3
import os

# Detect environment
if os.path.exists('/home/emonigatsaucee'):
    db_path = '/home/emonigatsaucee/wegatsauceefashionhub/instance/wegatsaucee.db'
else:
    db_path = 'instance/wegatsaucee.db'

print(f"Connecting to database: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Add likes_count column to product table
    print("\n1. Adding likes_count column to product table...")
    try:
        cursor.execute("ALTER TABLE product ADD COLUMN likes_count INTEGER DEFAULT 0")
        print("✓ likes_count column added successfully")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("✓ likes_count column already exists")
        else:
            print(f"✗ Error adding likes_count: {e}")
    
    # 2. Create newsletter table
    print("\n2. Creating newsletter table...")
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS newsletter (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(120) UNIQUE NOT NULL,
                subscribed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                active BOOLEAN DEFAULT 1
            )
        """)
        print("✓ Newsletter table created successfully")
    except sqlite3.OperationalError as e:
        print(f"✗ Error creating newsletter table: {e}")
    
    # 3. Initialize likes_count for existing products
    print("\n3. Initializing likes_count for existing products...")
    cursor.execute("UPDATE product SET likes_count = 0 WHERE likes_count IS NULL")
    updated = cursor.rowcount
    print(f"✓ Updated {updated} products")
    
    # Commit changes
    conn.commit()
    print("\n✅ Database migration completed successfully!")
    
    # Show summary
    print("\n📊 Database Summary:")
    cursor.execute("SELECT COUNT(*) FROM product")
    print(f"   Products: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM newsletter")
    print(f"   Newsletter subscribers: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM product WHERE likes_count > 0")
    print(f"   Products with likes: {cursor.fetchone()[0]}")
    
except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    import traceback
    traceback.print_exc()
finally:
    if conn:
        conn.close()
        print("\n✓ Database connection closed")

print("\n🎉 Done! Reload your web app on PythonAnywhere.")
