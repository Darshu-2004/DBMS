import mysql.connector
from datetime import datetime, timedelta
import random

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Darshu@2004",
    database="transport_system"
)
cursor = conn.cursor(dictionary=True)

# Get all routes without schedules
cursor.execute("""
    SELECT r.route_id, r.route_number, r.source, r.destination, r.distance_km, r.estimated_duration_mins
    FROM ksrtc_routes r
    LEFT JOIN ksrtc_schedules s ON r.route_id = s.route_id
    WHERE s.schedule_id IS NULL
""")

routes_without_schedules = cursor.fetchall()
print(f"Found {len(routes_without_schedules)} routes without schedules")

# Get available buses
cursor.execute("SELECT bus_id, bus_type FROM ksrtc_buses WHERE is_active = TRUE LIMIT 20")
buses = cursor.fetchall()
print(f"Found {len(buses)} active buses")

# Bus type to fare multiplier
fare_multipliers = {
    'VOLVO': 1.5,
    'ASHWAMEDHA': 1.4,
    'PALLAKKI': 1.3,
    'K/S': 1.0,
    'NON A/C SLEEPER': 0.9,
    'SUPER FAST': 1.2,
    'EXPRESS': 1.1
}

schedules_added = 0

for route in routes_without_schedules:
    route_id = route['route_id']
    distance = float(route['distance_km']) if route['distance_km'] else 100.0  # Default if null
    duration = route['estimated_duration_mins'] or 120  # Default if null
    
    # Calculate base fare based on distance
    base_fare = max(50, distance * 1.5)  # Minimum ₹50, ₹1.5 per km
    
    # Add 3 schedules per route with different buses and times
    departure_times = ['06:00:00', '13:00:00', '18:30:00']
    
    for i in range(3):
        bus = buses[i % len(buses)]
        bus_id = bus['bus_id']
        bus_type = bus['bus_type']
        
        # Calculate arrival time
        departure = datetime.strptime(departure_times[i], '%H:%M:%S')
        arrival = departure + timedelta(minutes=duration)
        arrival_time = arrival.strftime('%H:%M:%S')
        
        # Adjust fare based on bus type
        multiplier = fare_multipliers.get(bus_type, 1.0)
        schedule_fare = round(base_fare * multiplier, 2)
        
        # Insert schedule
        cursor.execute("""
            INSERT INTO ksrtc_schedules (route_id, bus_id, departure_time, arrival_time, base_fare, status)
            VALUES (%s, %s, %s, %s, %s, 'Active')
        """, (route_id, bus_id, departure_times[i], arrival_time, schedule_fare))
        
        schedules_added += 1

conn.commit()
print(f"\n✅ Successfully added {schedules_added} schedules to {len(routes_without_schedules)} routes!")

# Verify
cursor.execute("""
    SELECT COUNT(*) as total FROM ksrtc_routes r 
    LEFT JOIN ksrtc_schedules s ON r.route_id = s.route_id 
    WHERE s.schedule_id IS NULL
""")
remaining = cursor.fetchone()['total']
print(f"Routes still without schedules: {remaining}")

cursor.close()
conn.close()
