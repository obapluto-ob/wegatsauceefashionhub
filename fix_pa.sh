#!/bin/bash
# One-command fix for PythonAnywhere database error
# Run: bash fix_pa.sh

echo "🔧 Fixing PythonAnywhere Database..."

cd ~/wegatsauceefashionhub || exit 1
source ~/.virtualenvs/myenv/bin/activate || exit 1

mkdir -p instance
chmod 755 instance

python3 << 'EOF'
from app import app, db, Product

with app.app_context():
    db.create_all()
    if Product.query.count() == 0:
        products = [
            Product(name='Elegant Dress', price=2500, description='Beautiful floral dress', category='dresses', gender='women', stock=50, is_trending=True),
            Product(name='Chiffon Blouse', price=1800, description='Light chiffon top', category='tops', gender='women', stock=30, is_trending=True),
            Product(name='Business Suit', price=5500, description='Professional business suit', category='suits', gender='men', stock=20, is_trending=True),
            Product(name='Leather Shoes', price=3200, description='Comfortable leather shoes', category='shoes', gender='unisex', stock=25, is_trending=True),
            Product(name='Designer Handbag', price=4500, description='Premium leather handbag', category='accessories', gender='women', stock=15, is_trending=True),
            Product(name='Casual Shirt', price=1200, description='Cotton casual shirt', category='shirts', gender='men', stock=40, is_trending=True)
        ]
        for p in products:
            db.session.add(p)
        db.session.commit()
        print(f"✓ Added {len(products)} products")
    print("✅ Database ready!")
EOF

chmod 644 instance/wegatsaucee.db 2>/dev/null

echo ""
echo "✅ Fix complete!"
echo "📝 Now go to PythonAnywhere Web tab and click 'Reload'"
