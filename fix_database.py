import sqlite3
import os

# Connect to database
db_path = 'instance/turktrendy.db'
if not os.path.exists(db_path):
    print("Database not found!")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check current table structure
    cursor.execute('PRAGMA table_info("order")')
    columns = cursor.fetchall()
    existing_columns = [col[1] for col in columns]
    
    print("Current Order table columns:")
    for col in existing_columns:
        print(f"  - {col}")
    
    # Add missing columns if they don't exist
    if 'payment_method' not in existing_columns:
        cursor.execute('ALTER TABLE "order" ADD COLUMN payment_method VARCHAR(20)')
        print("Added payment_method column")
    else:
        print("payment_method column already exists")
    
    if 'payment_reference' not in existing_columns:
        cursor.execute('ALTER TABLE "order" ADD COLUMN payment_reference VARCHAR(100)')
        print("Added payment_reference column")
    else:
        print("payment_reference column already exists")
    
    conn.commit()
    print("Database updated successfully!")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()