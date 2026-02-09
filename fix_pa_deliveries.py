import sqlite3

db_path = '/home/emonigatsaucee/wegatsauceefashionhub/instance/wegatsaucee.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Update all orders with delivery confirmations to 'delivered' status
cursor.execute("""
    UPDATE "order" 
    SET status = 'delivered' 
    WHERE id IN (SELECT order_id FROM delivery_confirmation)
    AND status != 'delivered'
""")

updated = cursor.rowcount
conn.commit()
conn.close()

print(f"Updated {updated} orders to 'delivered' status")
