"""
Verify database setup and check all tables and data
"""

import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Darshu@2004',
    'database': 'transport_system'
}

def verify_database():
    print("\n" + "="*60)
    print("  DATABASE VERIFICATION")
    print("="*60 + "\n")
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check tables
        print("📋 Checking Tables...")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if tables:
            print(f"✓ Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("✗ No tables found!")
            return False
        
        print("\n📊 Checking Data...")
        
        # Check users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"✓ Users: {user_count}")
        
        # Check views
        print("\n🔍 Checking Analytics Views...")
        cursor.execute("SHOW FULL TABLES WHERE Table_type = 'VIEW'")
        views = cursor.fetchall()
        
        if views:
            print(f"✓ Found {len(views)} views:")
            for view in views:
                print(f"  - {view[0]}")
        else:
            print("⚠ No views found")
        
        # Show admin user
        print("\n👤 Admin User Details:")
        cursor.execute("SELECT username, email, user_type FROM users WHERE user_type = 'admin'")
        admin = cursor.fetchone()
        if admin:
            print(f"  Username: {admin[0]}")
            print(f"  Email: {admin[1]}")
            print(f"  Type: {admin[2]}")
            print(f"  Password: Admin@123 (default)")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("✅ Database verification completed successfully!")
        print("="*60 + "\n")
        
        return True
        
    except Error as e:
        print(f"\n✗ Error: {e}\n")
        return False

if __name__ == "__main__":
    verify_database()
