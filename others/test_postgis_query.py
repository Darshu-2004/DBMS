"""Test PostGIS query to see if it can find incidents near a Bangalore route"""
import psycopg2
from decimal import Decimal

DB_CONFIG = {
    'host': 'localhost',
    'database': 'routes',
    'user': 'postgres',
    'password': 'Darshu@2004',
    'port': 5432
}

# Sample route coordinates for Bangalore (near Majestic to MG Road area)
test_route = [
    [77.5714, 12.9770],  # Majestic
    [77.5946, 12.9716],  # MG Road
]

try:
    print("🔌 Connecting to PostgreSQL...")
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # First check: Do we have any incidents in Bangalore area?
    print("\n📊 Checking incidents in Bangalore area (lat: 12.9-13.0, lng: 77.5-77.7)...")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM incidents 
        WHERE latitude BETWEEN 12.9 AND 13.0 
        AND longitude BETWEEN 77.5 AND 77.7;
    """)
    bangalore_count = cursor.fetchone()[0]
    print(f"   Found {bangalore_count} incidents in Bangalore area")
    
    if bangalore_count > 0:
        print("\n📦 Sample Bangalore incidents:")
        cursor.execute("""
            SELECT id, ty, latitude, longitude, d
            FROM incidents 
            WHERE latitude BETWEEN 12.9 AND 13.0 
            AND longitude BETWEEN 77.5 AND 77.7
            LIMIT 5;
        """)
        for row in cursor.fetchall():
            print(f"   Type {row[1]}: ({row[2]}, {row[3]}) - {row[4]}")
    
    # Check what area the incidents actually cover
    print("\n🗺️  Overall incidents coverage:")
    cursor.execute("""
        SELECT 
            MIN(latitude), MAX(latitude),
            MIN(longitude), MAX(longitude),
            COUNT(*)
        FROM incidents;
    """)
    min_lat, max_lat, min_lng, max_lng, total = cursor.fetchone()
    print(f"   Latitude range: {min_lat} to {max_lat}")
    print(f"   Longitude range: {min_lng} to {max_lng}")
    print(f"   Total incidents: {total}")
    
    # Try the PostGIS query like in api.py
    print("\n🔍 Testing PostGIS ST_DWithin query...")
    
    # Build LINESTRING from route coordinates
    linestring_coords = ', '.join([f'{lng} {lat}' for lng, lat in test_route])
    linestring = f'LINESTRING({linestring_coords})'
    
    print(f"   Route: {linestring}")
    
    query = """
        SELECT 
            latitude,
            longitude,
            ty,
            d,
            id
        FROM incidents
        WHERE ST_DWithin(
            geom_indexed::geography,
            ST_GeomFromText(%s, 4326)::geography,
            200
        )
        ORDER BY latitude, longitude
        LIMIT 50;
    """
    
    cursor.execute(query, (linestring,))
    results = cursor.fetchall()
    
    print(f"\n✅ PostGIS query returned {len(results)} incidents within 200m")
    
    if results:
        print("\n📦 Incidents found near route:")
        for row in results[:5]:
            print(f"   Type {row[2]}: ({row[0]}, {row[1]}) - {row[3]}")
    else:
        print("\n⚠️  No incidents found near test route")
        print("   This is expected if incidents data is not for Bangalore area")
    
    # Check if geom_indexed column is properly populated
    print("\n🔍 Checking geom_indexed column...")
    cursor.execute("SELECT COUNT(*) FROM incidents WHERE geom_indexed IS NOT NULL;")
    geom_count = cursor.fetchone()[0]
    print(f"   {geom_count} out of {total} incidents have geom_indexed")
    
    if geom_count == 0:
        print("\n❌ PROBLEM FOUND: geom_indexed column is NULL for all incidents!")
        print("   Need to populate geom_indexed from latitude/longitude")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
