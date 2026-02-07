#!/usr/bin/env python3
"""
Quick Fix Script for PythonAnywhere Deployment
Run this script to fix all database and configuration issues
"""

import os
import sys
import sqlite3
from pathlib import Path

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def check_env_file():
    """Check if .env file exists and has required variables"""
    print_header("Checking Environment Configuration")
    
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ .env file not found!")
        print("\n📝 Creating .env file...")
        
        env_content = """# Flask Configuration
SECRET_KEY=wegatsaucee-secret-key-2024
SQLALCHEMY_DATABASE_URI=sqlite:///instance/wegatsaucee.db
ADMIN_USER=admin
ADMIN_PASS=admin123
"""
        env_path.write_text(env_content)
        print("✅ .env file created successfully!")
        return True
    else:
        print("✅ .env file exists")
        
        # Check if it has required variables
        content = env_path.read_text()
        required = ['ADMIN_USER', 'ADMIN_PASS', 'SECRET_KEY']
        missing = [var for var in required if var not in content]
        
        if missing:
            print(f"⚠️  Missing variables: {', '.join(missing)}")
            print("Please add them to your .env file")
            return False
        else:
            print("✅ All required variables present")
            return True

def ensure_instance_directory():
    """Create instance directory if it doesn't exist"""
    print_header("Checking Instance Directory")
    
    instance_dir = Path('instance')
    if not instance_dir.exists():
        print("📁 Creating instance directory...")
        instance_dir.mkdir(parents=True, exist_ok=True)
        print("✅ Instance directory created")
    else:
        print("✅ Instance directory exists")
    
    return True

def migrate_database():
    """Add missing columns to database"""
    print_header("Migrating Database")
    
    db_path = 'instance/wegatsaucee.db'
    
    if not os.path.exists(db_path):
        print(f"⚠️  Database not found at {db_path}")
        print("It will be created when you first run the app")
        return True
    
    print(f"🔧 Migrating: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        migrations = []
        
        # Check Product table
        cursor.execute("PRAGMA table_info(product)")
        product_columns = [col[1] for col in cursor.fetchall()]
        
        if 'flash_sale_price' not in product_columns:
            migrations.append(("ALTER TABLE product ADD COLUMN flash_sale_price REAL", "product.flash_sale_price"))
        
        if 'flash_sale_end' not in product_columns:
            migrations.append(("ALTER TABLE product ADD COLUMN flash_sale_end DATETIME", "product.flash_sale_end"))
        
        # Check Order table
        cursor.execute("PRAGMA table_info('order')")
        order_columns = [col[1] for col in cursor.fetchall()]
        
        if 'coupon_code' not in order_columns:
            migrations.append(("ALTER TABLE 'order' ADD COLUMN coupon_code VARCHAR(50)", "order.coupon_code"))
        
        if 'discount_amount' not in order_columns:
            migrations.append(("ALTER TABLE 'order' ADD COLUMN discount_amount REAL DEFAULT 0", "order.discount_amount"))
        
        # Execute migrations
        if not migrations:
            print("✅ Database is up to date!")
        else:
            for sql, description in migrations:
                try:
                    cursor.execute(sql)
                    print(f"✅ Added: {description}")
                except sqlite3.OperationalError as e:
                    if "duplicate column" in str(e).lower():
                        print(f"⚠️  Already exists: {description}")
                    else:
                        print(f"❌ Error: {description} - {e}")
            
            conn.commit()
            print(f"\n✨ Migration complete!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def fix_permissions():
    """Fix file permissions"""
    print_header("Fixing Permissions")
    
    try:
        db_path = Path('instance/wegatsaucee.db')
        if db_path.exists():
            os.chmod(db_path, 0o644)
            print("✅ Database permissions fixed")
        
        instance_dir = Path('instance')
        if instance_dir.exists():
            os.chmod(instance_dir, 0o755)
            print("✅ Instance directory permissions fixed")
        
        return True
    except Exception as e:
        print(f"⚠️  Could not fix permissions: {e}")
        return False

def verify_installation():
    """Verify the installation"""
    print_header("Verifying Installation")
    
    checks = []
    
    # Check .env
    checks.append((".env file", Path('.env').exists()))
    
    # Check instance directory
    checks.append(("instance directory", Path('instance').exists()))
    
    # Check database
    db_exists = Path('instance/wegatsaucee.db').exists()
    checks.append(("database file", db_exists))
    
    # Print results
    all_good = True
    for name, status in checks:
        symbol = "✅" if status else "❌"
        print(f"{symbol} {name}")
        if not status:
            all_good = False
    
    return all_good

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("  🚀 Wegatsaucee Fashion Hub - Quick Fix Script")
    print("="*60)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"\n📍 Working directory: {os.getcwd()}")
    
    # Run fixes
    steps = [
        ("Environment Configuration", check_env_file),
        ("Instance Directory", ensure_instance_directory),
        ("Database Migration", migrate_database),
        ("File Permissions", fix_permissions),
    ]
    
    results = []
    for step_name, step_func in steps:
        try:
            result = step_func()
            results.append((step_name, result))
        except Exception as e:
            print(f"❌ Error in {step_name}: {e}")
            results.append((step_name, False))
    
    # Final verification
    verify_installation()
    
    # Summary
    print_header("Summary")
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    print(f"✅ {success_count}/{total_count} steps completed successfully")
    
    if success_count == total_count:
        print("\n🎉 All fixes applied successfully!")
        print("\n📋 Next steps:")
        print("1. Reload your web app in PythonAnywhere dashboard")
        print("2. Visit your site to verify it works")
        print("3. Login to admin panel: /admin/login (admin/admin123)")
    else:
        print("\n⚠️  Some issues remain. Check the output above.")
        print("You may need to manually fix remaining issues.")
    
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    main()
