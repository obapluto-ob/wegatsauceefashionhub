#!/usr/bin/env python3
"""
Database Migration - Add Newsletter Table
Run this on both local and PythonAnywhere
"""

from app import app, db, Newsletter

def migrate_database():
    print("🔄 Starting database migration...")
    
    with app.app_context():
        try:
            # Create all tables (including Newsletter)
            db.create_all()
            print("✅ Newsletter table created successfully!")
            
            # Test the table
            count = Newsletter.query.count()
            print(f"✅ Newsletter table working! Current subscribers: {count}")
            
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

if __name__ == '__main__':
    success = migrate_database()
    if success:
        print("\n✅ Migration complete! Newsletter subscription should now work.")
    else:
        print("\n❌ Migration failed. Check the error above.")
