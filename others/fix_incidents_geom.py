"""Populate geom_indexed column from latitude/longitude for all incidents"""
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
    
    # Check current state
    cursor.execute("SELECT COUNT(*) FROM incidents WHERE geom_indexed IS NULL;")
    null_count = cursor.fetchone()[0]
    print(f"📊 Found {null_count} incidents with NULL geom_indexed")
    
    # Update geom_indexed from latitude/longitude
    print("\n🔧 Populating geom_indexed column...")
    update_query = """
        UPDATE incidents
        SET geom_indexed = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
        WHERE geom_indexed IS NULL
        AND latitude IS NOT NULL
        AND longitude IS NOT NULL;
    """
    
    cursor.execute(update_query)
    updated_count = cursor.rowcount
    conn.commit()
    
    print(f"✅ Updated {updated_count} incidents")
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM incidents WHERE geom_indexed IS NOT NULL;")
    geom_count = cursor.fetchone()[0]
    print(f"📊 Now {geom_count} incidents have geom_indexed")
    
    # Create spatial index if it doesn't exist
    print("\n🔧 Ensuring spatial index exists...")
    try:
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS incidents_geom_idx 
            ON incidents USING GIST (geom_indexed);
        """)
        conn.commit()
        print("✅ Spatial index created/verified")
    except Exception as e:
        print(f"⚠️  Index creation note: {e}")
        conn.rollback()
    
    # Test the query again
    print("\n🔍 Testing PostGIS query with Bangalore route...")
    test_linestring = 'LINESTRING(77.5714 12.977, 77.5946 12.9716)'
    
    cursor.execute("""
        SELECT COUNT(*)
        FROM incidents
        WHERE ST_DWithin(
            geom_indexed::geography,
            ST_GeomFromText(%s, 4326)::geography,
            200
        );
    """, (test_linestring,))
    
    count = cursor.fetchone()[0]
    print(f"✅ Found {count} incidents within 200m of test route")
    
    # Show sample results
    if count > 0:
        cursor.execute("""
            SELECT latitude, longitude, ty, d
            FROM incidents
            WHERE ST_DWithin(
                geom_indexed::geography,
                ST_GeomFromText(%s, 4326)::geography,
                200
            )
            LIMIT 5;
        """, (test_linestring,))
        
        print("\n📦 Sample incidents:")
        for row in cursor.fetchall():
            print(f"   Type {row[2]}: ({row[0]}, {row[1]}) - {row[3]}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ Incidents table is now ready for route optimization!")
    print("   The route search should now show incident counts correctly.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
