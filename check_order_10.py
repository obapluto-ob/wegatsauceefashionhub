import sqlite3

db_path = '/home/emonigatsaucee/wegatsauceefashionhub/instance/wegatsaucee.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check order 10
cursor.execute("SELECT id, status FROM \"order\" WHERE id = 10")
order = cursor.fetchone()
if order:
    print(f"Order #{order[0]} - Current status: {order[1]}")
else:
    print("Order #10 not found")

# Check if delivery confirmation exists for order 10
cursor.execute("SELECT id, order_id, rating FROM delivery_confirmation WHERE order_id = 10")
conf = cursor.fetchone()
if conf:
    print(f"Delivery confirmation exists: ID={conf[0]}, Rating={conf[2]}")
else:
    print("No delivery confirmation found for order #10")

conn.close()
