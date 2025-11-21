"""
Quick KSRTC Sample Data Population
"""
from database import execute_query, execute_query_one
from datetime import time

# Sample stops
stops = [
    'BANGALORE MAJESTIC', 'MYSURU', 'SHIVAMOGGA', 'MANGALORE', 'HASSAN',
    'MADIKERI', 'HUBLI', 'BELGAUM', 'DAVANGERE', 'TUMKUR',
    'MANDYA', 'CHICKMAGALUR', 'UDUPI', 'SIRSI', 'KARWAR',
    'K.R. PURAM', 'MARATHAHALLI', 'SILK BOARD', 'ELECTRONIC CITY'
]

# Sample routes with timings
routes = [
    {'route': 'KA0001', 'from': 'BANGALORE MAJESTIC', 'to': 'MYSURU', 'type': 'VOLVO', 'time': '06:00', 'fare': 450},
    {'route': 'KA0002', 'from': 'BANGALORE MAJESTIC', 'to': 'MYSURU', 'type': 'K/S', 'time': '07:30', 'fare': 280},
    {'route': 'KA0003', 'from': 'BANGALORE MAJESTIC', 'to': 'MANGALORE', 'type': 'VOLVO', 'time': '21:30', 'fare': 850},
    {'route': 'KA0004', 'from': 'BANGALORE MAJESTIC', 'to': 'MANGALORE', 'type': 'NON A/C SLEEPER', 'time': '22:00', 'fare': 650},
    {'route': 'KA0005', 'from': 'BANGALORE MAJESTIC', 'to': 'SHIVAMOGGA', 'type': 'K/S', 'time': '08:00', 'fare': 350},
    {'route': 'KA0006', 'from': 'BANGALORE MAJESTIC', 'to': 'HUBLI', 'type': 'ASHWAMEDHA', 'time': '22:30', 'fare': 720},
    {'route': 'KA0007', 'from': 'MYSURU', 'to': 'BANGALORE MAJESTIC', 'type': 'VOLVO', 'time': '06:30', 'fare': 450},
    {'route': 'KA0008', 'from': 'MYSURU', 'to': 'MANGALORE', 'type': 'K/S', 'time': '07:00', 'fare': 550},
    {'route': 'KA0009', 'from': 'HASSAN', 'to': 'BANGALORE MAJESTIC', 'type': 'K/S', 'time': '09:00', 'fare': 300},
    {'route': 'KA0010', 'from': 'SHIVAMOGGA', 'to': 'BANGALORE MAJESTIC', 'type': 'VOLVO', 'time': '05:30', 'fare': 520},
]

def populate_quick_data():
    print("Inserting stops...")
    for stop in stops:
        execute_query(
            "INSERT IGNORE INTO ksrtc_stops (stop_name, is_major_stop) VALUES (%s, TRUE)",
            (stop,)
        )
    print(f"[OK] {len(stops)} stops inserted")
    
    print("\nInserting routes, buses, and schedules...")
    for route_data in routes:
        # Insert route
        execute_query(
            """INSERT IGNORE INTO ksrtc_routes (route_number, source, destination, distance_km)
               VALUES (%s, %s, %s, %s)""",
            (route_data['route'], route_data['from'], route_data['to'], 150)
        )
        route_id = execute_query_one(
            "SELECT route_id FROM ksrtc_routes WHERE route_number = %s",
            (route_data['route'],)
        )['route_id']
        
        # Insert bus
        bus_number = f"BUS{route_data['route']}"
        bus_type = route_data['type']
        seats = 40 if bus_type in ['K/S', 'R/H'] else 45
        ac = bus_type in ['VOLVO', 'ASHWAMEDHA', 'PALLAKKI']
        
        execute_query(
            """INSERT IGNORE INTO ksrtc_buses 
               (bus_number, bus_type, total_seats, seater_seats, ac_available)
               VALUES (%s, %s, %s, %s, %s)""",
            (bus_number, bus_type, seats, seats, ac)
        )
        bus_id = execute_query_one(
            "SELECT bus_id FROM ksrtc_buses WHERE bus_number = %s",
            (bus_number,)
        )['bus_id']
        
        # Insert schedule
        execute_query(
            """INSERT IGNORE INTO ksrtc_schedules (route_id, bus_id, departure_time, base_fare)
               VALUES (%s, %s, %s, %s)""",
            (route_id, bus_id, route_data['time'], route_data['fare'])
        )
        
        # Insert seats
        for seat_num in range(1, seats + 1):
            execute_query(
                """INSERT IGNORE INTO ksrtc_seats (bus_id, seat_number, seat_type, seat_row, seat_column)
                   VALUES (%s, %s, 'Seater', %s, %s)""",
                (bus_id, f"{seat_num}", (seat_num-1)//4 + 1, chr(65 + (seat_num-1)%4))
            )
        
        print(f"  Route {route_data['route']}: {route_data['from']} -> {route_data['to']}")
    
    print(f"\n[OK] Sample KSRTC data populated successfully!")
    print(f"  - {len(stops)} stops")
    print(f"  - {len(routes)} routes with buses and schedules")

if __name__ == "__main__":
    populate_quick_data()
