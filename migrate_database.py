import sqlite3

# Connect to database
conn = sqlite3.connect('instance/wegatsaucee.db')
cursor = conn.cursor()

print("Starting migration...\n")

try:
    cursor.execute('ALTER TABLE user ADD COLUMN points INTEGER DEFAULT 0')
    print("✓ Added user.points")
except Exception as e:
    print(f"user.points: {e}")

try:
    cursor.execute('ALTER TABLE user ADD COLUMN tier VARCHAR(20) DEFAULT "bronze"')
    print("✓ Added user.tier")
except Exception as e:
    print(f"user.tier: {e}")

try:
    cursor.execute('ALTER TABLE user ADD COLUMN admin_rating INTEGER DEFAULT 0')
    print("✓ Added user.admin_rating")
except Exception as e:
    print(f"user.admin_rating: {e}")

try:
    cursor.execute('ALTER TABLE "order" ADD COLUMN shipping_fee FLOAT DEFAULT 0')
    print("✓ Added order.shipping_fee")
except Exception as e:
    print(f"order.shipping_fee: {e}")

try:
    cursor.execute('ALTER TABLE "order" ADD COLUMN commission FLOAT DEFAULT 0')
    print("✓ Added order.commission")
except Exception as e:
    print(f"order.commission: {e}")

try:
    cursor.execute('ALTER TABLE "order" ADD COLUMN items TEXT')
    print("✓ Added order.items")
except Exception as e:
    print(f"order.items: {e}")

try:
    cursor.execute('ALTER TABLE "order" ADD COLUMN cancellation_reason TEXT')
    print("✓ Added order.cancellation_reason")
except Exception as e:
    print(f"order.cancellation_reason: {e}")

try:
    cursor.execute('ALTER TABLE "order" ADD COLUMN expected_delivery TIMESTAMP')
    print("✓ Added order.expected_delivery")
except Exception as e:
    print(f"order.expected_delivery: {e}")

try:
    cursor.execute('ALTER TABLE product ADD COLUMN sizes TEXT')
    print("✓ Added product.sizes")
except Exception as e:
    print(f"product.sizes: {e}")

try:
    cursor.execute('ALTER TABLE product ADD COLUMN colors TEXT')
    print("✓ Added product.colors")
except Exception as e:
    print(f"product.colors: {e}")

try:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            location VARCHAR(200),
            transport_company VARCHAR(100),
            driver_name VARCHAR(100),
            status VARCHAR(50),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES "order" (id)
        )
    ''')
    print("✓ Created order_tracking table")
except Exception as e:
    print(f"order_tracking: {e}")

try:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS delivery_confirmation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            photo_url VARCHAR(500),
            rating INTEGER,
            feedback TEXT,
            confirmed_by_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES "order" (id),
            FOREIGN KEY (user_id) REFERENCES user (id)
        )
    ''')
    print("✓ Created delivery_confirmation table")
except Exception as e:
    print(f"delivery_confirmation: {e}")

try:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wishlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user (id),
            FOREIGN KEY (product_id) REFERENCES product (id)
        )
    ''')
    print("✓ Created wishlist table")
except Exception as e:
    print(f"wishlist: {e}")

try:
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recently_viewed (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user (id),
            FOREIGN KEY (product_id) REFERENCES product (id)
        )
    ''')
    print("✓ Created recently_viewed table")
except Exception as e:
    print(f"recently_viewed: {e}")

conn.commit()
conn.close()

print("\n✓ Migration complete!")
print("Run: python app.py")
