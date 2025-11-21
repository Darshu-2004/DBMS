"""Check if incidents table exists in PostgreSQL routes database"""
import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'database': 'routes',
    'user': 'postgres',
    'password': 'Darshu@2004',
    'port': 5432
}

try:
    print("🔌 Connecting to PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    
    print("\n📊 Tables in 'routes' database:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check if incidents table exists
    table_names = [t[0] for t in tables]
    if 'incidents' in table_names:
        print("\n✅ incidents table EXISTS")
        
        # Count rows
        cursor.execute("SELECT COUNT(*) FROM incidents;")
        count = cursor.fetchone()[0]
        print(f"📊 Row count: {count}")
        
        # Show columns
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'incidents'
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        print("\n📋 Columns:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
        
        # Sample data
        if count > 0:
            cursor.execute("SELECT * FROM incidents LIMIT 5;")
            rows = cursor.fetchall()
            print(f"\n📦 Sample data (first {len(rows)} rows):")
            for row in rows:
                print(f"  {row}")
    else:
        print("\n❌ incidents table DOES NOT EXIST")
        print("\n💡 Need to create incidents table for route optimization feature")
    
    # Check PostGIS extension
    cursor.execute("SELECT PostGIS_Version();")
    postgis_version = cursor.fetchone()[0]
    print(f"\n🗺️  PostGIS version: {postgis_version}")
    
    cursor.close()
    conn.close()
    print("\n✅ Check complete")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
