import mysql.connector
import json
import csv
from datetime import datetime, time

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Darshu@2004",
    database="transport_system"
)
cursor = conn.cursor(dictionary=True)

print("🚂 Starting Train and Flight Import...")

# Clear existing data
print("\n📋 Clearing old train data...")
cursor.execute("DELETE FROM train_schedules")
cursor.execute("DELETE FROM train_running_days")
cursor.execute("DELETE FROM trains")
cursor.execute("DELETE FROM train_stations WHERE 1=1")
conn.commit()

# Import Train Stations and Trains
station_map = {}
train_count = 0

for train_file in ['PASS-TRAINS.json', 'EXP-TRAINS.json', 'SF-TRAINS.json']:
    print(f"\n📂 Processing {train_file}...")
    
    try:
        with open(train_file, 'r', encoding='utf-8') as f:
            trains_data = json.load(f)
        
        for idx, train in enumerate(trains_data):
            if idx >= 100:  # Limit to 100 trains per file
                break
                
            try:
                train_number = train['trainNumber']
                train_name = train['trainName']
                
                # Determine train type
                if 'PASS' in train_file:
                    train_type = 'Passenger'
                elif 'SF' in train_file:
                    train_type = 'Superfast'
                else:
                    train_type = 'Express'
                
                # Insert train
                cursor.execute("""
                    INSERT INTO trains (train_number, train_name, train_type)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE train_name = VALUES(train_name)
                """, (train_number, train_name, train_type))
                
                train_id = cursor.lastrowid or cursor.execute("SELECT train_id FROM trains WHERE train_number = %s", (train_number,)) or cursor.fetchone()['train_id']
                
                # Insert running days
                running_days = train.get('runningDays', {})
                cursor.execute("""
                    INSERT INTO train_running_days (train_id, sunday, monday, tuesday, wednesday, thursday, friday, saturday)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    train_id,
                    running_days.get('SUN', True),
                    running_days.get('MON', True),
                    running_days.get('TUE', True),
                    running_days.get('WED', True),
                    running_days.get('THU', True),
                    running_days.get('FRI', True),
                    running_days.get('SAT', True)
                ))
                
                # Process route
                for stop in train.get('trainRoute', []):
                    station_name = stop['stationName']
                    station_code = station_name.split(' - ')[-1] if ' - ' in station_name else station_name[:3].upper()
                    station_city = station_name.split(' - ')[0] if ' - ' in station_name else station_name
                    
                    # Add station if not exists
                    if station_code not in station_map:
                        cursor.execute("""
                            INSERT INTO train_stations (code, name, city)
                            VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE name = VALUES(name)
                        """, (station_code, station_name, station_city))
                        station_map[station_code] = True
                    
                    # Parse times
                    arrival_str = stop.get('arrives', 'Source')
                    departure_str = stop.get('departs', 'Destination')
                    
                    arrival_time = None
                    departure_time = None
                    
                    if arrival_str not in ['Source', 'NA', '']:
                        try:
                            arrival_time = datetime.strptime(arrival_str, '%H:%M').time()
                        except:
                            pass
                    
                    if departure_str not in ['Destination', 'NA', '']:
                        try:
                            departure_time = datetime.strptime(departure_str, '%H:%M').time()
                        except:
                            pass
                    
                    # Insert schedule
                    cursor.execute("""
                        INSERT INTO train_schedules (train_id, station_code, stop_number, arrival_time, departure_time, distance_km, day_count)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        train_id,
                        station_code,
                        int(stop.get('sno', 1)),
                        arrival_time,
                        departure_time,
                        float(stop.get('distance', 0)) if stop.get('distance') else 0,
                        int(stop.get('dayCount', 1)) if stop.get('dayCount') else 1
                    ))
                
                train_count += 1
                if train_count % 10 == 0:
                    print(f"  ✓ Imported {train_count} trains...")
                    
            except Exception as e:
                print(f"  ✗ Error with train {train.get('trainNumber', 'unknown')}: {e}")
                continue
        
        conn.commit()
        print(f"✅ Completed {train_file} - Total trains: {train_count}")
        
    except Exception as e:
        print(f"❌ Error processing {train_file}: {e}")

print(f"\n🎉 Train import complete! Total: {train_count} trains, {len(station_map)} stations")

# Import Flights
print("\n✈️ Starting Flight Import...")
print("📋 Clearing old flight data...")
cursor.execute("DELETE FROM flight_schedules")
cursor.execute("DELETE FROM flights")
cursor.execute("DELETE FROM airports WHERE 1=1")
cursor.execute("DELETE FROM airlines WHERE 1=1")
conn.commit()

# Track cities and airlines
city_airports = {}
airlines_map = {}

try:
    with open('Flight_Schedule.csv', 'r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f)
        flight_count = 0
        
        for idx, row in enumerate(csv_reader):
            if idx >= 500:  # Limit to 500 flights
                break
            
            try:
                airline = row['airline']
                flight_num = row['flightNumber']
                origin = row['origin']
                destination = row['destination']
                dept_time_str = row['scheduledDepartureTime']
                arr_time_str = row['scheduledArrivalTime']
                days_str = row['daysOfWeek']
                
                # Add airline
                if airline not in airlines_map:
                    airline_code = airline[:2].upper()
                    cursor.execute("""
                        INSERT INTO airlines (airline_code, airline_name, country)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE airline_name = VALUES(airline_name)
                    """, (airline_code, airline, 'India'))
                    cursor.execute("SELECT airline_id FROM airlines WHERE airline_code = %s", (airline_code,))
                    airlines_map[airline] = cursor.fetchone()['airline_id']
                
                # Add airports
                for city in [origin, destination]:
                    if city not in city_airports:
                        airport_code = city[:3].upper()
                        cursor.execute("""
                            INSERT INTO airports (airport_code, airport_name, city, country)
                            VALUES (%s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE airport_name = VALUES(airport_name)
                        """, (airport_code, f"{city} Airport", city, 'India'))
                        city_airports[city] = airport_code
                
                # Parse times
                dept_time = None
                arr_time = None
                
                if dept_time_str and dept_time_str != 'NA':
                    try:
                        dept_time = datetime.strptime(dept_time_str, '%H:%M').time()
                    except:
                        pass
                
                if arr_time_str and arr_time_str != 'NA':
                    try:
                        arr_time = datetime.strptime(arr_time_str, '%H:%M').time()
                    except:
                        pass
                
                if not dept_time:
                    continue
                
                # Calculate duration
                if dept_time and arr_time:
                    dept_mins = dept_time.hour * 60 + dept_time.minute
                    arr_mins = arr_time.hour * 60 + arr_time.minute
                    duration = arr_mins - dept_mins
                    if duration < 0:
                        duration += 1440  # Add 24 hours
                else:
                    duration = 120  # Default 2 hours
                
                # Insert flight
                cursor.execute("""
                    INSERT INTO flights (airline_id, flight_number, origin_code, destination_code, 
                                       departure_time, arrival_time, flight_duration_mins)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    airlines_map[airline],
                    f"{airline[:2].upper()}{flight_num}",
                    city_airports[origin],
                    city_airports[destination],
                    dept_time,
                    arr_time,
                    duration
                ))
                
                flight_id = cursor.lastrowid
                
                # Parse days of week
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
                    INSERT INTO flight_schedules (flight_id, sunday, monday, tuesday, wednesday, thursday, friday, saturday, valid_from, valid_to)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    flight_id,
                    schedule_days['sunday'],
                    schedule_days['monday'],
                    schedule_days['tuesday'],
                    schedule_days['wednesday'],
                    schedule_days['thursday'],
                    schedule_days['friday'],
                    schedule_days['saturday'],
                    '2025-11-01',
                    '2025-12-31'
                ))
                
                flight_count += 1
                if flight_count % 50 == 0:
                    print(f"  ✓ Imported {flight_count} flights...")
                    
            except Exception as e:
                print(f"  ✗ Error with flight: {e}")
                continue
        
        conn.commit()
        print(f"\n✅ Flight import complete! Total: {flight_count} flights, {len(city_airports)} airports")
        
except Exception as e:
    print(f"❌ Error processing flights: {e}")

cursor.close()
conn.close()

print("\n🎉 ALL DONE! Database updated successfully!")
print(f"📊 Summary: {train_count} trains, {len(station_map)} stations, {len(city_airports)} airports")
