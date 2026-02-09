#!/usr/bin/env python3
"""
PythonAnywhere Database Fix
Run this on PythonAnywhere to fix database path issues
"""

import os
import sys
import shutil
from pathlib import Path

def fix_pythonanywhere_database():
    print("🔧 Fixing PythonAnywhere Database...")
    
    # Get the project directory
    project_dir = Path('/home/emonigatsaucee/wegatsauceefashionhub')
    
    # Create instance directory if it doesn't exist
    instance_dir = project_dir / 'instance'
    instance_dir.mkdir(exist_ok=True)
    print(f"✓ Instance directory: {instance_dir}")
    
    # Set proper permissions
    os.chmod(instance_dir, 0o755)
    print(f"✓ Set permissions on instance directory")
    
    # Database file path
    db_file = instance_dir / 'wegatsaucee.db'
    
    # If database doesn't exist, create it
    if not db_file.exists():
        print("📦 Creating new database...")
        
        # Import app and create tables
        sys.path.insert(0, str(project_dir))
        os.chdir(project_dir)
        
        from app import app, db, Product
        
        with app.app_context():
            db.create_all()
            print("✓ Database tables created")
            
            # Add sample products if none exist
            if Product.query.count() == 0:
                print("📦 Adding sample products...")
                sample_products = [
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
                for product in sample_products:
                    db.session.add(product)
                db.session.commit()
                print(f"✓ Added {len(sample_products)} sample products")
    else:
        print(f"✓ Database exists: {db_file}")
    
    # Set database file permissions
    if db_file.exists():
        os.chmod(db_file, 0o644)
        print(f"✓ Set permissions on database file")
    
    print("\n✅ Fix complete! Now reload your web app in PythonAnywhere dashboard.")
    print("\n📝 Next steps:")
    print("1. Go to PythonAnywhere Web tab")
    print("2. Click 'Reload' button")
    print("3. Visit your site")

if __name__ == '__main__':
    try:
        fix_pythonanywhere_database()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n🔍 Troubleshooting:")
        print("1. Make sure you're running this on PythonAnywhere")
        print("2. Check that the path /home/emonigatsaucee/wegatsauceefashionhub exists")
        print("3. Verify your virtual environment is activated")
        sys.exit(1)
