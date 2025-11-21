"""Import KSRTC routes from Excel file to database"""
import pandas as pd
import mysql.connector
from datetime import datetime, time
import re

# Database connection
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Darshu@2004',
    'database': 'transport_system'
}

def normalize_city_name(name):
    """Normalize city names"""
    if pd.isna(name):
        return None
    
    name = str(name).strip().upper()
    
    # Fix common variations
    replacements = {
        'SHIVAMOGG': 'SHIVAMOGGA',
        'SHIVAMOGA': 'SHIVAMOGGA',
        'SHIMOGA': 'SHIVAMOGGA',
        'BANGLORE': 'BANGALORE',
        'BENGALURU': 'BANGALORE',
        'SRRSI': 'SIRSI',
        'GOKRNA': 'GOKARNA',
        'DONDELI': 'DANDELI',
        'KARWARA': 'KARWAR'
    }
    
    return replacements.get(name, name)

def parse_time(time_val):
    """Parse time from Excel format"""
    if pd.isna(time_val):
        return None
    
    # If it's already a time object
    if isinstance(time_val, time):
        return time_val
    
    # If it's a float (Excel time format)
    if isinstance(time_val, (int, float)):
        hours = int(time_val)
        minutes = int((time_val - hours) * 60)
        if hours >= 24:
            hours = hours % 24
        return f"{hours:02d}:{minutes:02d}:00"
    
    # If it's a string
    time_str = str(time_val).strip()
    # Try to extract HH:MM or HH.MM format
    match = re.match(r'(\d+)[:\.](\d+)', time_str)
    if match:
        hours, minutes = int(match.group(1)), int(match.group(2))
        if hours >= 24:
            hours = hours % 24
        return f"{hours:02d}:{minutes:02d}:00"
    
    return "08:00:00"  # Default time

def normalize_bus_type(service_class):
    """Normalize bus type names"""
    if pd.isna(service_class):
        return 'ORDINARY'
    
    sc = str(service_class).strip().upper()
    
    if 'VOLVO' in sc or 'A/C SLEEPER' in sc or 'AC SLEEPER' in sc:
        return 'VOLVO'
    elif 'NON A/C SLEEPER' in sc or 'NON AC SLEEPER' in sc:
        return 'NON A/C SLEEPER'
    elif 'PALLAKKI' in sc or 'PALAKE' in sc:
        return 'PALLAKKI'
    elif 'K/S' in sc or 'KS' in sc:
        return 'K/S'
    elif 'AIRAVAT' in sc:
        return 'AIRAVAT'
    else:
        return 'ORDINARY'

# Connect to database
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor(dictionary=True)

# Read Excel file
print("Reading Excel file...")
df = pd.read_excel('SHIVAMOGGA_1762846076.xlsx', skiprows=2)
df.columns = ['SL_NO', 'FROM', 'TO', 'SERVICE_CLASS', 'VIA_PLACES', 'DEPARTURE_TIME']

print(f"Total rows in Excel: {len(df)}")

# Clean data
df['FROM'] = df['FROM'].apply(normalize_city_name)
df['TO'] = df['TO'].apply(normalize_city_name)
df['SERVICE_CLASS'] = df['SERVICE_CLASS'].apply(normalize_bus_type)
df['DEPARTURE_TIME'] = df['DEPARTURE_TIME'].apply(parse_time)

# Remove rows with invalid data
df = df.dropna(subset=['FROM', 'TO'])
df = df[df['FROM'] != df['TO']]

print(f"Valid routes after cleaning: {len(df)}")

# Get all unique cities
all_cities = set(df['FROM'].unique()) | set(df['TO'].unique())
print(f"\nTotal unique cities: {len(all_cities)}")

# First, ensure all stops exist
print("\nInserting stops...")
for city in sorted(all_cities):
    try:
        cursor.execute("""
            INSERT IGNORE INTO ksrtc_stops (stop_name, is_major_stop)
            VALUES (%s, 1)
        """, (city,))
    except Exception as e:
        print(f"Error inserting stop {city}: {e}")

conn.commit()
print(f"✓ {len(all_cities)} stops inserted/verified")

# Get all existing buses
cursor.execute("SELECT bus_id, bus_number, bus_type FROM ksrtc_buses WHERE is_active = 1")
buses = cursor.fetchall()
print(f"\nAvailable buses: {len(buses)}")

# Prepare fare mapping
fare_map = {
    'VOLVO': 350,
    'AIRAVAT': 400,
    'PALLAKKI': 320,
    'NON A/C SLEEPER': 250,
    'K/S': 180,
    'ORDINARY': 150
}

# Insert routes and schedules
print("\nInserting routes and schedules...")
route_count = 0
schedule_count = 0

for idx, row in df.iterrows():
    try:
        source = row['FROM']
        destination = row['TO']
        bus_type = row['SERVICE_CLASS']
        departure = row['DEPARTURE_TIME']
        via = row['VIA_PLACES'] if not pd.isna(row['VIA_PLACES']) else None
        
        # Create route number
        route_number = f"SM{route_count+1:04d}"
        
        # Insert route
        cursor.execute("""
            INSERT INTO ksrtc_routes 
            (route_number, source, destination, distance_km, estimated_duration_mins, via_places, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, 1)
        """, (route_number, source, destination, 100, 180, via))
        
        route_id = cursor.lastrowid
        route_count += 1
        
        # Find a bus of matching type
        matching_buses = [b for b in buses if b['bus_type'] == bus_type]
        if not matching_buses:
            matching_buses = buses  # Use any bus if no match
        
        bus = matching_buses[0]
        base_fare = fare_map.get(bus_type, 200)
        
        # Calculate arrival time (add 3-4 hours)
        dep_parts = departure.split(':')
        dep_hour = int(dep_parts[0])
        arrival_hour = (dep_hour + 3) % 24
        arrival_time = f"{arrival_hour:02d}:{dep_parts[1]}:00"
        
        # Insert schedule
        cursor.execute("""
            INSERT INTO ksrtc_schedules 
            (route_id, bus_id, departure_time, arrival_time, base_fare, status)
            VALUES (%s, %s, %s, %s, %s, 'Active')
        """, (route_id, bus['bus_id'], departure, arrival_time, base_fare))
        
        schedule_count += 1
        
        if (idx + 1) % 50 == 0:
            print(f"  Processed {idx + 1}/{len(df)} routes...")
            conn.commit()
            
    except Exception as e:
        print(f"Error processing row {idx}: {e}")
        continue

conn.commit()
print(f"\n✓ Successfully imported:")
print(f"  - {route_count} routes")
print(f"  - {schedule_count} schedules")

# Verify
cursor.execute("SELECT COUNT(*) as count FROM ksrtc_routes")
print(f"\nTotal routes in database: {cursor.fetchone()['count']}")

cursor.execute("SELECT COUNT(*) as count FROM ksrtc_schedules")
print(f"Total schedules in database: {cursor.fetchone()['count']}")

cursor.close()
conn.close()

print("\n✅ Import completed successfully!")
