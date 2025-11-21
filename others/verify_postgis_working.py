"""Test with a larger search area to verify PostGIS is working"""
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
    
    # Find where most Bangalore incidents are concentrated
    print("📊 Finding incident clusters in Bangalore...")
    cursor.execute("""
        SELECT 
            ROUND(latitude::numeric, 2) as lat_group,
            ROUND(longitude::numeric, 2) as lng_group,
            COUNT(*) as incident_count
        FROM incidents
        WHERE latitude BETWEEN 12.9 AND 13.0 
        AND longitude BETWEEN 77.5 AND 77.7
        GROUP BY lat_group, lng_group
        ORDER BY incident_count DESC
        LIMIT 5;
    """)
    
    clusters = cursor.fetchall()
    print("\nTop incident clusters:")
    for lat, lng, count in clusters:
        print(f"   ({lat}, {lng}): {count} incidents")
    
    if clusters:
        # Test with coordinates near the biggest cluster
        hot_lat, hot_lng, _ = clusters[0]
        
        # Create a route that passes through this area
        test_route = [
            [float(hot_lng) - 0.01, float(hot_lat) - 0.01],
            [float(hot_lng), float(hot_lat)],
            [float(hot_lng) + 0.01, float(hot_lat) + 0.01],
        ]
        
        linestring_coords = ', '.join([f'{lng} {lat}' for lng, lat in test_route])
        linestring = f'LINESTRING({linestring_coords})'
        
        print(f"\n🔍 Testing route through hotspot: {linestring}")
        
        # Try with larger radius
        for radius in [200, 500, 1000, 2000]:
            cursor.execute("""
                SELECT COUNT(*)
                FROM incidents
                WHERE ST_DWithin(
                    geom_indexed::geography,
                    ST_GeomFromText(%s, 4326)::geography,
                    %s
                );
            """, (linestring, radius))
            
            count = cursor.fetchone()[0]
            print(f"   Radius {radius}m: {count} incidents")
        
        # Show the actual incidents found with 2000m radius
        print("\n📦 Incidents found (2000m radius):")
        cursor.execute("""
            SELECT latitude, longitude, ty, d, id
            FROM incidents
            WHERE ST_DWithin(
                geom_indexed::geography,
                ST_GeomFromText(%s, 4326)::geography,
                2000
            )
            LIMIT 10;
        """, (linestring,))
        
        for row in cursor.fetchall():
            print(f"   Type {row[2]}: ({row[0]}, {row[1]}) - {row[3][:30] if row[3] else 'No desc'}")
    
    cursor.close()
    conn.close()
    print("\n✅ PostGIS spatial queries are working!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
