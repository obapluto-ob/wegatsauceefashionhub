import sqlite3
import os
from pathlib import Path

# Create .env file
env_content = """SECRET_KEY=wegatsaucee-secret-key-2024
SQLALCHEMY_DATABASE_URI=sqlite:///instance/wegatsaucee.db
ADMIN_USER=admin
ADMIN_PASS=admin123
"""
Path('.env').write_text(env_content)
print("✅ .env created")

# Create instance directory
Path('instance').mkdir(exist_ok=True)
print("✅ instance directory ready")

# Migrate database
db_path = 'instance/wegatsaucee.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    migrations = [
        "ALTER TABLE product ADD COLUMN flash_sale_price REAL",
        "ALTER TABLE product ADD COLUMN flash_sale_end DATETIME",
        "ALTER TABLE 'order' ADD COLUMN coupon_code VARCHAR(50)",
        "ALTER TABLE 'order' ADD COLUMN discount_amount REAL DEFAULT 0"
    ]
    
    for sql in migrations:
        try:
            cursor.execute(sql)
            print(f"✅ {sql.split('ADD COLUMN')[1].strip()}")
        except:
            pass
    
    conn.commit()
    conn.close()
    print("✨ Migration complete!")
else:
    print("⚠️  Database will be created on first run")

print("\n🎉 Done! Now reload your web app.")
