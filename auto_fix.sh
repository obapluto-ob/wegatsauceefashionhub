#!/bin/bash
# One-Command Fix for PythonAnywhere Deployment
# Run this script to fix all issues automatically

echo "=========================================="
echo "  Wegatsaucee Fashion Hub - Auto Fix"
echo "=========================================="
echo ""

# Navigate to project directory
cd ~/wegatsauceefashionhub || { echo "❌ Project directory not found"; exit 1; }
echo "✅ Found project directory"

# Activate virtual environment
source ~/.virtualenvs/myenv/bin/activate || { echo "❌ Virtual environment not found"; exit 1; }
echo "✅ Virtual environment activated"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
SECRET_KEY=wegatsaucee-secret-key-2024
SQLALCHEMY_DATABASE_URI=sqlite:////home/emonigatsaucee/wegatsauceefashionhub/instance/wegatsaucee.db
ADMIN_USER=admin
ADMIN_PASS=admin123
EOF
    echo "✅ .env file created"
else
    echo "✅ .env file exists"
fi

# Create instance directory
mkdir -p instance
echo "✅ Instance directory ready"

# Check if database exists, create if not
if [ ! -f instance/wegatsaucee.db ]; then
    echo "📦 Creating database..."
    python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Database created')"
fi

# Run database migration
echo "🔧 Running database migration..."
python << 'PYTHON_SCRIPT'
import sqlite3
import os

db_path = 'instance/wegatsaucee.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    migrations = [
        ("ALTER TABLE product ADD COLUMN flash_sale_price REAL", "product.flash_sale_price"),
        ("ALTER TABLE product ADD COLUMN flash_sale_end DATETIME", "product.flash_sale_end"),
        ("ALTER TABLE 'order' ADD COLUMN coupon_code VARCHAR(50)", "order.coupon_code"),
        ("ALTER TABLE 'order' ADD COLUMN discount_amount REAL DEFAULT 0", "order.discount_amount"),
    ]
    
    for sql, desc in migrations:
        try:
            cursor.execute(sql)
            print(f"✅ Added: {desc}")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print(f"⚠️  Already exists: {desc}")
            else:
                print(f"❌ Error: {desc}")
    
    conn.commit()
    conn.close()
    print("✨ Migration complete!")
else:
    print("⚠️  Database not found, will be created on first run")
PYTHON_SCRIPT

# Fix permissions
chmod 755 instance 2>/dev/null
chmod 644 instance/wegatsaucee.db 2>/dev/null
echo "✅ Permissions fixed"

# Verify installation
echo ""
echo "=========================================="
echo "  Verification"
echo "=========================================="

python << 'VERIFY_SCRIPT'
import os
from pathlib import Path

checks = [
    (".env file", Path('.env').exists()),
    ("instance directory", Path('instance').exists()),
    ("database file", Path('instance/wegatsaucee.db').exists()),
]

for name, status in checks:
    symbol = "✅" if status else "❌"
    print(f"{symbol} {name}")
VERIFY_SCRIPT

echo ""
echo "=========================================="
echo "  ✨ Fix Complete!"
echo "=========================================="
echo ""
echo "📋 Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Click the green 'Reload' button"
echo "3. Visit your site to test"
echo "4. Admin login: /admin/login (admin/admin123)"
echo ""
