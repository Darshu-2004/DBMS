import mysql.connector
import csv
from datetime import datetime

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Darshu@2004",
    database="transport_system"
)
cursor = conn.cursor(dictionary=True)

print("✈️  Importing Flights from Flight_Schedule.csv...")

# Track unique cities and airlines
airports_map = {}
airlines_map = {}
flight_count = 0

try:
    with open('Flight_Schedule.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Debug: Check header
        fieldnames = reader.fieldnames
        print(f"📋 CSV Headers: {fieldnames}")
        
        for idx, row in enumerate(reader):
            if idx >= 500:  # Limit to 500 flights
                break
            
            try:
                # Debug first row
                if idx == 0:
                    print(f"🔍 First row keys: {list(row.keys())}")
                    print(f"🔍 First row sample: {dict(list(row.items())[:3])}")
                
                airline = row['airline'].strip('"') if 'airline' in row else row.get(list(row.keys())[0], '').strip('"')
                flight_num = row['flightNumber'].strip('"') if 'flightNumber' in row else row.get(list(row.keys())[1], '').strip('"')
                origin = row['origin'].strip('"') if 'origin' in row else row.get(list(row.keys())[2], '').strip('"')
                dest = row['destination'].strip('"') if 'destination' in row else row.get(list(row.keys())[3], '').strip('"')
                dept_str = row['scheduledDepartureTime'].strip('"') if 'scheduledDepartureTime' in row else row.get(list(row.keys())[5], '').strip('"')
                arr_str = row['scheduledArrivalTime'].strip('"') if 'scheduledArrivalTime' in row else row.get(list(row.keys())[6], '').strip('"')
                days_str = row['daysOfWeek'].strip('"') if 'daysOfWeek' in row else row.get(list(row.keys())[4], '').strip('"')
                
                # Skip if no departure time
                if not dept_str or dept_str == 'NA':
                    continue
                
                # Add airline
                if airline not in airlines_map:
                    airline_code = airline[:2].upper() if len(airline) >= 2 else airline[0].upper() + 'X'
                    cursor.execute("""
                        INSERT INTO airlines (airline_code, airline_name, country) 
                        VALUES (%s, %s, 'India')
                        ON DUPLICATE KEY UPDATE airline_name = VALUES(airline_name)
                    """, (airline_code, airline))
                    cursor.execute("SELECT airline_id FROM airlines WHERE airline_code = %s", (airline_code,))
                    result = cursor.fetchone()
                    airlines_map[airline] = result['airline_id']
                
                # Add airports
                for city in [origin, dest]:
                    if city not in airports_map:
                        code = city[:3].upper()
                        cursor.execute("""
                            INSERT INTO airports (airport_code, airport_name, city, country)
                            VALUES (%s, %s, %s, 'India')
                            ON DUPLICATE KEY UPDATE airport_name = VALUES(airport_name)
                        """, (code, f"{city} Airport", city))
                        airports_map[city] = code
                
                # Parse times
                dept_time = datetime.strptime(dept_str, '%H:%M').time() if dept_str and dept_str != 'NA' else None
                arr_time = datetime.strptime(arr_str, '%H:%M').time() if arr_str and arr_str != 'NA' else None
                
                if not dept_time:
                    continue
                
                # Calculate duration
                if dept_time and arr_time:
                    dept_mins = dept_time.hour * 60 + dept_time.minute
                    arr_mins = arr_time.hour * 60 + arr_time.minute
                    duration = arr_mins - dept_mins
                    if duration < 0:
                        duration += 1440
                else:
                    duration = 120
                
                # Insert flight
                cursor.execute("""
                    INSERT INTO flights (airline_id, flight_number, origin_code, destination_code,
                                       departure_time, arrival_time, flight_duration_mins)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    airlines_map[airline],
                    f"{airline[:2].upper()}{flight_num}",
                    airports_map[origin],
                    airports_map[dest],
                    dept_time,
                    arr_time,
                    duration
                ))
                
                flight_id = cursor.lastrowid
                
                # Parse days
                days_map = {
                    'Sunday': 'sunday', 'Monday': 'monday', 'Tuesday': 'tuesday',
                    'Wednesday': 'wednesday', 'Thursday': 'thursday',
                    'Friday': 'friday', 'Saturday': 'saturday'
                }
                
                schedule_days = {day: False for day in days_map.values()}
                for full_day, db_day in days_map.items():
                    if full_day in days_str:
                        schedule_days[db_day] = True
                
                # Insert schedule
                cursor.execute("""
                    INSERT INTO flight_schedules (flight_id, sunday, monday, tuesday, wednesday,
                                                 thursday, friday, saturday, valid_from, valid_to)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, '2025-11-01', '2025-12-31')
                """, (
                    flight_id,
                    schedule_days['sunday'],
                    schedule_days['monday'],
                    schedule_days['tuesday'],
                    schedule_days['wednesday'],
                    schedule_days['thursday'],
                    schedule_days['friday'],
                    schedule_days['saturday']
                ))
                
                flight_count += 1
                if flight_count % 50 == 0:
                    print(f"  ✓ Imported {flight_count} flights...")
                    conn.commit()
                    
            except Exception as e:
                print(f"  ✗ Error: {e}")
                continue
        
        conn.commit()
        print(f"\n✅ Flight import complete!")
        print(f"   Flights: {flight_count}")
        print(f"   Airports: {len(airports_map)}")
        print(f"   Airlines: {len(airlines_map)}")
        
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    cursor.close()
    conn.close()
