"""
Database Migration Script for PythonAnywhere Deployment
Adds missing columns to existing database tables
"""

import sqlite3
import os
from datetime import datetime

def migrate_database(db_path='instance/wegatsaucee.db'):
    """Add missing columns to database tables"""
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False
    
    print(f"🔧 Migrating database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    migrations = []
    
    # Check and add missing columns to Product table
    cursor.execute("PRAGMA table_info(product)")
    product_columns = [col[1] for col in cursor.fetchall()]
    
    if 'flash_sale_price' not in product_columns:
        migrations.append(("ALTER TABLE product ADD COLUMN flash_sale_price REAL", "product.flash_sale_price"))
    
    if 'flash_sale_end' not in product_columns:
        migrations.append(("ALTER TABLE product ADD COLUMN flash_sale_end DATETIME", "product.flash_sale_end"))
    
    # Check and add missing columns to Order table
    cursor.execute("PRAGMA table_info('order')")
    order_columns = [col[1] for col in cursor.fetchall()]
    
    if 'coupon_code' not in order_columns:
        migrations.append(("ALTER TABLE 'order' ADD COLUMN coupon_code VARCHAR(50)", "order.coupon_code"))
    
    if 'discount_amount' not in order_columns:
        migrations.append(("ALTER TABLE 'order' ADD COLUMN discount_amount REAL DEFAULT 0", "order.discount_amount"))
    
    # Execute migrations
    success_count = 0
    for sql, description in migrations:
        try:
            cursor.execute(sql)
            print(f"✅ Added column: {description}")
            success_count += 1
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"⚠️  Column already exists: {description}")
            else:
                print(f"❌ Error adding {description}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✨ Migration complete! {success_count} columns added.")
    return True

if __name__ == '__main__':
    # Try both local and production paths
    paths = [
        'instance/wegatsaucee.db',
        '/home/emonigatsaucee/wegatsauceefashionhub/instance/wegatsaucee.db',
        'wegatsaucee.db'
    ]
    
    migrated = False
    for path in paths:
        if os.path.exists(path):
            print(f"\n📍 Found database at: {path}")
            migrate_database(path)
            migrated = True
            break
    
    if not migrated:
        print("\n❌ No database found. Please check your database path.")
        print("Available paths checked:")
        for path in paths:
            print(f"  - {path}")
