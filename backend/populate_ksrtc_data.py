"""
Populate KSRTC database with data from PDFs
"""
from database import execute_query, execute_query_one
import re
from datetime import time
import random

def clean_stop_name(name):
    """Clean and standardize stop names"""
    name = name.strip().upper()
    # Remove extra spaces
    name = re.sub(r'\s+', ' ', name)
    return name

def parse_time(time_str):
    """Parse time string to time object"""
    try:
        time_str = time_str.strip().replace("'", ":").replace(".", ":")
        time_str = re.sub(r'[^\d:]', '', time_str)
        
        if not time_str:
            return None
            
        parts = time_str.split(':')
        if len(parts) == 1:
            hour = int(parts[0])
            minute = 0
        else:
            hour = int(parts[0]) if parts[0] else 0
            minute = int(parts[1]) if len(parts) > 1 and parts[1] else 0
        
        # Handle 24+ hours
        hour = hour % 24
        minute = min(minute, 59)
        
        return time(hour, minute)
    except:
        return None

def get_bus_type_details(bus_type):
    """Get bus configuration based on type"""
    config = {
        'K/S': {'total_seats': 40, 'seater': 40, 'sleeper': 0, 'ac': False},
        'VOLVO': {'total_seats': 45, 'seater': 45, 'sleeper': 0, 'ac': True},
        'NON A/C SLEEPER': {'total_seats': 35, 'seater': 0, 'sleeper': 35, 'ac': False},
        'PALLAKKI': {'total_seats': 40, 'seater': 40, 'sleeper': 0, 'ac': True},
        'ASHWAMEDHA': {'total_seats': 45, 'seater': 45, 'sleeper': 0, 'ac': True},
        'R/H': {'total_seats': 40, 'seater': 40, 'sleeper': 0, 'ac': False},
        'EV': {'total_seats': 40, 'seater': 40, 'sleeper': 0, 'ac': True}
    }
    return config.get(bus_type, {'total_seats': 40, 'seater': 40, 'sleeper': 0, 'ac': False})

def calculate_fare(source, destination, bus_type, distance_km=None):
    """Calculate dynamic fare based on route and bus type"""
    # Base fare multipliers
    multipliers = {
        'K/S': 1.0,
        'VOLVO': 1.8,
        'NON A/C SLEEPER': 1.3,
        'PALLAKKI': 1.6,
        'ASHWAMEDHA': 1.7,
        'R/H': 1.1,
        'EV': 1.5
    }
    
    # Estimate distance if not provided
    if not distance_km:
        # Simple estimation based on city pairs
        if 'BANGLORE' in destination or 'BANGALORE' in destination:
            distance_km = random.randint(250, 400)
        else:
            distance_km = random.randint(50, 200)
    
    # Base rate: ₹2.5 per km
    base_fare = distance_km * 2.5
    multiplier = multipliers.get(bus_type, 1.0)
    final_fare = base_fare * multiplier
    
    # Ensure minimum fare of ₹200
    return max(200.0, round(final_fare, 2))

def populate_from_pdf_text():
    """Populate database from extracted PDF text"""
    
    # Read the extracted text
    with open('shivamogga_text.txt', 'r', encoding='utf-8') as f:
        shivamogga_lines = f.readlines()
    
    with open('mysuru_text.txt', 'r', encoding='utf-8') as f:
        mysuru_lines = f.readlines()
    
    all_stops = set()
    routes_data = []
    
    # Parse Shivamogga routes
    print("Parsing Shivamogga routes...")
    for line in shivamogga_lines:
        line = line.strip()
        if not line or 'SL NO' in line or 'FROM' in line:
            continue
        
        # Try to match route pattern
        parts = re.split(r'\s{2,}', line)
        if len(parts) >= 5:
            try:
                source = clean_stop_name(parts[1] if len(parts) > 1 else '')
                destination = clean_stop_name(parts[2] if len(parts) > 2 else '')
                bus_type = parts[3].strip() if len(parts) > 3 else 'K/S'
                time_str = parts[-1] if len(parts) > 0 else ''
                
                if source and destination and source != destination:
                    all_stops.add(source)
                    all_stops.add(destination)
                    
                    dept_time = parse_time(time_str)
                    if dept_time:
                        routes_data.append({
                            'source': source,
                            'destination': destination,
                            'bus_type': bus_type,
                            'departure_time': dept_time,
                            'via': parts[4] if len(parts) > 4 else '',
                            'city': 'SHIVAMOGGA'
                        })
            except:
                continue
    
    # Parse Mysuru routes (similar logic)
    print("Parsing Mysuru routes...")
    for line in mysuru_lines:
        line = line.strip()
        if not line or 'SL NO' in line or 'FROM' in line:
            continue
        
        parts = re.split(r'\s{2,}', line)
        if len(parts) >= 5:
            try:
                source = clean_stop_name(parts[1] if len(parts) > 1 else '')
                destination = clean_stop_name(parts[2] if len(parts) > 2 else '')
                bus_type = parts[3].strip() if len(parts) > 3 else 'K/S'
                time_str = parts[-1]
                
                if source and destination and source != destination:
                    all_stops.add(source)
                    all_stops.add(destination)
                    
                    dept_time = parse_time(time_str)
                    if dept_time:
                        routes_data.append({
                            'source': source,
                            'destination': destination,
                            'bus_type': bus_type,
                            'departure_time': dept_time,
                            'via': parts[4] if len(parts) > 4 else '',
                            'city': 'MYSURU'
                        })
            except:
                continue
    
    print(f"\nFound {len(all_stops)} unique stops")
    print(f"Found {len(routes_data)} routes")
    
    # Insert stops
    print("\nInserting stops into database...")
    for stop_name in all_stops:
        try:
            execute_query(
                "INSERT IGNORE INTO ksrtc_stops (stop_name, is_major_stop) VALUES (%s, %s)",
                (stop_name, 'BANGALORE' in stop_name or 'MYSURU' in stop_name or 'SHIVAMOGGA' in stop_name)
            )
        except Exception as e:
            print(f"Error inserting stop {stop_name}: {e}")
    
    print("✓ Stops inserted")
    
    # Create routes and schedules
    print("\nCreating routes and schedules...")
    route_counter = 1
    bus_counter = 1
    
    for idx, route_info in enumerate(routes_data[:500], 1):  # Limit to 500 routes for demo
        try:
            # Create route
            route_number = f"KA{route_counter:04d}"
            source = route_info['source']
            dest = route_info['destination']
            
            # Check if route exists
            existing = execute_query_one(
                "SELECT route_id FROM ksrtc_routes WHERE source = %s AND destination = %s",
                (source, dest)
            )
            
            if not existing:
                execute_query(
                    """INSERT INTO ksrtc_routes (route_number, source, destination, via_places, distance_km)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (route_number, source, dest, route_info['via'], random.randint(50, 400))
                )
                route_id = execute_query_one("SELECT LAST_INSERT_ID() as id")['id']
                route_counter += 1
            else:
                route_id = existing['route_id']
            
            # Create bus
            bus_number = f"KA{route_info['city'][:2]}{bus_counter:04d}"
            bus_type = route_info['bus_type']
            config = get_bus_type_details(bus_type)
            
            execute_query(
                """INSERT IGNORE INTO ksrtc_buses 
                   (bus_number, bus_type, total_seats, seater_seats, sleeper_seats, ac_available)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (bus_number, bus_type, config['total_seats'], config['seater'], 
                 config['sleeper'], config['ac'])
            )
            bus_id = execute_query_one("SELECT bus_id FROM ksrtc_buses WHERE bus_number = %s", (bus_number,))['bus_id']
            bus_counter += 1
            
            # Create schedule
            fare = calculate_fare(source, dest, bus_type)
            execute_query(
                """INSERT INTO ksrtc_schedules (route_id, bus_id, departure_time, base_fare)
                   VALUES (%s, %s, %s, %s)""",
                (route_id, bus_id, route_info['departure_time'], fare)
            )
            
            # Create seats for this bus
            for seat_num in range(1, config['total_seats'] + 1):
                seat_type = 'Sleeper' if config['sleeper'] > 0 else 'Seater'
                execute_query(
                    """INSERT IGNORE INTO ksrtc_seats (bus_id, seat_number, seat_type, seat_row, seat_column)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (bus_id, f"{seat_num}", seat_type, (seat_num-1)//4 + 1, chr(65 + (seat_num-1)%4))
                )
            
            if idx % 50 == 0:
                print(f"  Processed {idx} routes...")
                
        except Exception as e:
            print(f"Error processing route {idx}: {e}")
            continue
    
    print(f"\n✓ Database populated successfully!")
    print(f"  - Routes created: {route_counter - 1}")
    print(f"  - Buses created: {bus_counter - 1}")
    print(f"  - Stops: {len(all_stops)}")

if __name__ == "__main__":
    populate_from_pdf_text()
