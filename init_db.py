#!/usr/bin/env python3
"""
Database Initialization Script for PythonAnywhere
Run this after uploading files: python3 init_db.py
"""

import os
import sys

# Ensure instance folder exists
os.makedirs('instance', exist_ok=True)
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('logs', exist_ok=True)

print("✓ Created necessary folders")

# Import app and database
try:
    from app import app, db, Product
    print("✓ Successfully imported app modules")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nMake sure you've installed requirements:")
    print("  pip3 install --user -r requirements.txt")
    sys.exit(1)

# Create database tables
try:
    with app.app_context():
        db.create_all()
        print("✓ Database tables created")
        
        # Check if products exist
        product_count = Product.query.count()
        print(f"✓ Current products in database: {product_count}")
        
        if product_count == 0:
            print("\n⚠ No products found. Add sample products? (y/n)")
            response = input().lower()
            if response == 'y':
                sample_products = [
                    Product(name='Elegant Dress', price=2500, description='Beautiful floral dress', 
                           category='dresses', gender='women', stock=50, is_trending=True),
                    Product(name='Chiffon Blouse', price=1800, description='Light chiffon top', 
                           category='tops', gender='women', stock=30, is_trending=True),
                    Product(name='Business Suit', price=5500, description='Professional business suit', 
                           category='suits', gender='men', stock=20, is_trending=True),
                    Product(name='Leather Shoes', price=3200, description='Comfortable leather shoes', 
                           category='shoes', gender='unisex', stock=25, is_trending=True),
                ]
                for product in sample_products:
                    db.session.add(product)
                db.session.commit()
                print(f"✓ Added {len(sample_products)} sample products")
        
        print("\n✅ Database initialization complete!")
        print("\nYou can now:")
        print("  1. Reload your web app on PythonAnywhere")
        print("  2. Visit your site")
        print("  3. Login to admin panel: /admin/login (admin/admin123)")
        
except Exception as e:
    print(f"\n✗ Database error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
