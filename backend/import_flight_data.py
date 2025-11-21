"""
Import flight data from CSV file
"""
import csv
import os
from database import execute_query, get_db_connection
from datetime import datetime

def parse_days_of_week(days_str):
    """Parse 'Monday,Tuesday,Wednesday' into boolean dict"""
    days_map = {
        'Sunday': 'sunday',
        'Monday': 'monday',
        'Tuesday': 'tuesday',
        'Wednesday': 'wednesday',
        'Thursday': 'thursday',
        'Friday': 'friday',
        'Saturday': 'saturday'
    }
    
    result = {day: False for day in days_map.values()}
    
    if not days_str:
        return result
    
    day_list = [d.strip() for d in days_str.split(',')]
    for day in day_list:
        if day in days_map:
            result[days_map[day]] = True
    
    return result

def import_flights_from_csv(csv_file):
    """Import flights from CSV file"""
    print(f"\nProcessing {csv_file}...")
    
    if not os.path.exists(csv_file):
        print(f"[ERROR] File not found: {csv_file}")
        return
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        flights_data = list(reader)
    
    total_flights = len(flights_data)
    print(f"Found {total_flights} flight records")
    
    # Limit to first 200 flights for demo
    flights_data = flights_data[:200]
    print(f"Importing first {len(flights_data)} flights...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    airports_added = set()
    airlines_added = set()
    flights_added = 0
    
    for idx, flight in enumerate(flights_data, 1):
        try:
            airline = flight.get('airline', '').strip()
            flight_number = flight.get('flightNumber', '').strip()
            origin = flight.get('origin', '').strip()
            destination = flight.get('destination', '').strip()
            days_of_week = flight.get('daysOfWeek', '')
            dept_time = flight.get('scheduledDepartureTime', '').strip()
            arr_time = flight.get('scheduledArrivalTime', '').strip()
            timezone = flight.get('timezone', '').strip()
            valid_from = flight.get('validFrom', '')
            valid_to = flight.get('validTo', '')
            
            if not airline or not flight_number or not origin or not destination:
                continue
            
            # Add airports
            for airport_city in [origin, destination]:
                if airport_city and airport_city not in airports_added:
                    airport_code = airport_city[:3].upper()
                    cursor.execute("""
                        INSERT IGNORE INTO airports 
                        (airport_code, airport_name, city, timezone)
                        VALUES (%s, %s, %s, %s)
                    """, (airport_code, f"{airport_city} Airport", airport_city, timezone or 'Asia/Kolkata'))
                    airports_added.add(airport_city)
            
            # Add airline
            if airline not in airlines_added:
                airline_code = airline[:2].upper()
                cursor.execute("""
                    INSERT IGNORE INTO airlines 
                    (airline_name, airline_code)
                    VALUES (%s, %s)
                """, (airline, airline_code))
                airlines_added.add(airline)
            
            # Get airline_id
            cursor.execute("SELECT airline_id FROM airlines WHERE airline_name = %s", (airline,))
            airline_row = cursor.fetchone()
            if not airline_row:
                continue
            airline_id = airline_row[0]
            
            # Parse times
            if dept_time and dept_time != 'NA':
                try:
                    dept_time_obj = datetime.strptime(dept_time, '%H:%M').time()
                except:
                    dept_time_obj = None
            else:
                dept_time_obj = None
            
            if arr_time and arr_time != 'NA':
                try:
                    arr_time_obj = datetime.strptime(arr_time, '%H:%M').time()
                except:
                    arr_time_obj = None
            else:
                arr_time_obj = None
            
            origin_code = origin[:3].upper()
            dest_code = destination[:3].upper()
            
            # Add flight
            cursor.execute("""
                INSERT INTO flights 
                (airline_id, flight_number, origin_code, destination_code, 
                 departure_time, arrival_time, economy_seats, business_seats, total_seats)
                VALUES (%s, %s, %s, %s, %s, %s, 150, 20, 170)
            """, (airline_id, flight_number, origin_code, dest_code, dept_time_obj, arr_time_obj))
            
            flight_id = cursor.lastrowid
            flights_added += 1
            
            # Parse running days
            days_dict = parse_days_of_week(days_of_week)
            
            # Parse valid dates
            valid_from_date = None
            valid_to_date = None
            if valid_from:
                try:
                    valid_from_date = datetime.strptime(valid_from, '%Y-%m-%d').date()
                except:
                    pass
            if valid_to:
                try:
                    valid_to_date = datetime.strptime(valid_to, '%Y-%m-%d').date()
                except:
                    pass
            
            # Add schedule
            cursor.execute("""
                INSERT INTO flight_schedules 
                (flight_id, sunday, monday, tuesday, wednesday, thursday, friday, saturday,
                 valid_from, valid_to)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                flight_id,
                days_dict['sunday'],
                days_dict['monday'],
                days_dict['tuesday'],
                days_dict['wednesday'],
                days_dict['thursday'],
                days_dict['friday'],
                days_dict['saturday'],
                valid_from_date,
                valid_to_date
            ))
            
            if idx % 50 == 0:
                print(f"  Processed {idx}/{len(flights_data)} flights...")
                conn.commit()
        
        except Exception as e:
            print(f"  [ERROR] Flight {flight_number}: {e}")
            continue
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"[OK] Imported {flights_added} flights, {len(airports_added)} airports, {len(airlines_added)} airlines")

def create_flight_seats():
    """Create seats for all flights"""
    print("\nCreating flight seats...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all flights
    cursor.execute("SELECT flight_id, economy_seats, business_seats FROM flights")
    flights = cursor.fetchall()
    
    seats_created = 0
    
    for flight in flights:
        flight_id = flight[0]
        economy_count = flight[1]
        business_count = flight[2]
        
        # Business seats (rows 1-5, columns A-D)
        row_num = 1
        for i in range(business_count):
            col = ['A', 'B', 'C', 'D'][i % 4]
            seat_num = f"{row_num}{col}"
            is_window = col in ['A', 'D']
            is_aisle = col in ['B', 'C']
            
            cursor.execute("""
                INSERT INTO flight_seats 
                (flight_id, seat_number, seat_class, seat_row, seat_column, is_window, is_aisle)
                VALUES (%s, %s, 'Business', %s, %s, %s, %s)
            """, (flight_id, seat_num, row_num, col, is_window, is_aisle))
            seats_created += 1
            
            if (i + 1) % 4 == 0:
                row_num += 1
        
        # Economy seats (rows 6-30, columns A-F)
        row_num = 6
        for i in range(economy_count):
            col = ['A', 'B', 'C', 'D', 'E', 'F'][i % 6]
            seat_num = f"{row_num}{col}"
            is_window = col in ['A', 'F']
            is_aisle = col in ['C', 'D']
            
            cursor.execute("""
                INSERT INTO flight_seats 
                (flight_id, seat_number, seat_class, seat_row, seat_column, is_window, is_aisle)
                VALUES (%s, %s, 'Economy', %s, %s, %s, %s)
            """, (flight_id, seat_num, row_num, col, is_window, is_aisle))
            seats_created += 1
            
            if (i + 1) % 6 == 0:
                row_num += 1
        
        if flight_id % 50 == 0:
            print(f"  Processed {flight_id} flights...")
            conn.commit()
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"[OK] Created {seats_created} seats")

if __name__ == "__main__":
    print("=" * 60)
    print("FLIGHT DATA IMPORT")
    print("=" * 60)
    
    # Get path to CSV file (one level up from backend folder)
    base_path = os.path.join(os.path.dirname(__file__), '..')
    
    import_flights_from_csv(os.path.join(base_path, 'Flight_Schedule.csv'))
    create_flight_seats()
    
    print("\n[OK] Flight data import completed!")
