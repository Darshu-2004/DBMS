"""
Import train data from JSON files
"""
import json
import os
from database import execute_query, get_db_connection

def parse_station_name(station_full):
    """Extract station name and code from 'STATION NAME - CODE' format"""
    if ' - ' in station_full:
        parts = station_full.rsplit(' - ', 1)
        return parts[0].strip(), parts[1].strip()
    return station_full.strip(), station_full[:3].upper()

def import_trains_from_json(json_file, train_type):
    """Import trains from a single JSON file"""
    print(f"\nProcessing {json_file} ({train_type})...")
    
    if not os.path.exists(json_file):
        print(f"[ERROR] File not found: {json_file}")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        trains_data = json.load(f)
    
    total_trains = len(trains_data)
    print(f"Found {total_trains} trains in {json_file}")
    
    # Limit to first 100 trains per file for demo (300 total)
    trains_data = trains_data[:100]
    print(f"Importing first {len(trains_data)} trains...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    stations_added = set()
    trains_added = 0
    schedules_added = 0
    
    for idx, train in enumerate(trains_data, 1):
        try:
            train_number = train.get('trainNumber', '').strip()
            train_name = train.get('trainName', '').strip()
            train_route = train.get('trainRoute', [])
            running_days = train.get('runningDays', {})
            
            if not train_number or not train_name or not train_route:
                continue
            
            # Get source and destination
            source_full = train_route[0].get('stationName', '')
            dest_full = train_route[-1].get('stationName', '')
            
            source_name, source_code = parse_station_name(source_full)
            dest_name, dest_code = parse_station_name(dest_full)
            
            # Add stations
            for station_data in train_route:
                st_full = station_data.get('stationName', '')
                st_name, st_code = parse_station_name(st_full)
                
                if st_code not in stations_added:
                    cursor.execute("""
                        INSERT IGNORE INTO train_stations 
                        (station_name, station_code, city) 
                        VALUES (%s, %s, %s)
                    """, (st_name, st_code, st_name.split()[0] if st_name else 'Unknown'))
                    stations_added.add(st_code)
            
            # Add train
            cursor.execute("""
                INSERT IGNORE INTO trains 
                (train_number, train_name, train_type, source_station_code, destination_station_code,
                 ac_1_coaches, ac_2_coaches, ac_3_coaches, sleeper_coaches, general_coaches)
                VALUES (%s, %s, %s, %s, %s, 2, 4, 6, 8, 2)
            """, (train_number, train_name, train_type, source_code, dest_code))
            
            if cursor.rowcount > 0:
                trains_added += 1
                train_id = cursor.lastrowid
                
                # Add running days
                cursor.execute("""
                    INSERT INTO train_running_days 
                    (train_id, sunday, monday, tuesday, wednesday, thursday, friday, saturday)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    train_id,
                    running_days.get('SUN', False),
                    running_days.get('MON', False),
                    running_days.get('TUE', False),
                    running_days.get('WED', False),
                    running_days.get('THU', False),
                    running_days.get('FRI', False),
                    running_days.get('SAT', False)
                ))
                
                # Add schedules
                for stop in train_route:
                    st_full = stop.get('stationName', '')
                    _, st_code = parse_station_name(st_full)
                    
                    arrival = stop.get('arrives', 'Source')
                    departure = stop.get('departs', 'Destination')
                    distance = stop.get('distance', '0 kms').replace(' kms', '').replace(',', '')
                    day = stop.get('day', '1')
                    sno = stop.get('sno', '1')
                    
                    # Parse times
                    arrival_time = None if arrival == 'Source' else arrival
                    departure_time = None if departure == 'Destination' else departure
                    
                    try:
                        distance_km = float(distance) if distance else 0.0
                    except:
                        distance_km = 0.0
                    
                    cursor.execute("""
                        INSERT INTO train_schedules 
                        (train_id, station_code, arrival_time, departure_time, distance_km, day_number, stop_number)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (train_id, st_code, arrival_time, departure_time, distance_km, int(day), int(sno)))
                    schedules_added += 1
            
            if idx % 20 == 0:
                print(f"  Processed {idx}/{len(trains_data)} trains...")
                conn.commit()
        
        except Exception as e:
            print(f"  [ERROR] Train {train_number}: {e}")
            continue
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"[OK] Imported {trains_added} trains, {len(stations_added)} unique stations, {schedules_added} schedules")

def create_sample_coaches():
    """Create coaches and berths for all trains"""
    print("\nCreating coaches and berths...")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all trains
    cursor.execute("SELECT train_id, ac_1_coaches, ac_2_coaches, ac_3_coaches, sleeper_coaches, general_coaches FROM trains")
    trains = cursor.fetchall()
    
    coaches_created = 0
    berths_created = 0
    
    for train in trains:
        train_id = train[0]
        ac1_count = train[1]
        ac2_count = train[2]
        ac3_count = train[3]
        sleeper_count = train[4]
        general_count = train[5]
        
        # AC-1 coaches (A1, A2...)
        for i in range(1, ac1_count + 1):
            coach_num = f"A{i}"
            cursor.execute("""
                INSERT INTO train_coaches (train_id, coach_number, coach_type, total_berths)
                VALUES (%s, %s, 'AC-1', 18)
            """, (train_id, coach_num))
            coach_id = cursor.lastrowid
            coaches_created += 1
            
            # 18 berths in AC-1
            for berth in range(1, 19):
                berth_type = 'LOWER' if berth % 4 == 1 else ('MIDDLE' if berth % 4 == 2 else 'UPPER')
                cursor.execute("""
                    INSERT INTO train_berths (coach_id, berth_number, berth_type)
                    VALUES (%s, %s, %s)
                """, (coach_id, str(berth), berth_type))
                berths_created += 1
        
        # AC-2 coaches
        for i in range(1, ac2_count + 1):
            coach_num = f"A{ac1_count + i}"
            cursor.execute("""
                INSERT INTO train_coaches (train_id, coach_number, coach_type, total_berths)
                VALUES (%s, %s, 'AC-2', 48)
            """, (train_id, coach_num))
            coach_id = cursor.lastrowid
            coaches_created += 1
            
            for berth in range(1, 49):
                berth_type = 'LOWER' if berth % 4 == 1 else ('MIDDLE' if berth % 4 == 2 else 'UPPER')
                cursor.execute("""
                    INSERT INTO train_berths (coach_id, berth_number, berth_type)
                    VALUES (%s, %s, %s)
                """, (coach_id, str(berth), berth_type))
                berths_created += 1
        
        # AC-3 coaches
        for i in range(1, ac3_count + 1):
            coach_num = f"B{i}"
            cursor.execute("""
                INSERT INTO train_coaches (train_id, coach_number, coach_type, total_berths)
                VALUES (%s, %s, 'AC-3', 72)
            """, (train_id, coach_num))
            coach_id = cursor.lastrowid
            coaches_created += 1
            
            for berth in range(1, 73):
                berth_type = 'LOWER' if berth % 8 in [1,4] else ('MIDDLE' if berth % 8 in [2,5] else 'UPPER')
                cursor.execute("""
                    INSERT INTO train_berths (coach_id, berth_number, berth_type)
                    VALUES (%s, %s, %s)
                """, (coach_id, str(berth), berth_type))
                berths_created += 1
        
        # Sleeper coaches
        for i in range(1, sleeper_count + 1):
            coach_num = f"S{i}"
            cursor.execute("""
                INSERT INTO train_coaches (train_id, coach_number, coach_type, total_berths)
                VALUES (%s, %s, 'SLEEPER', 72)
            """, (train_id, coach_num))
            coach_id = cursor.lastrowid
            coaches_created += 1
            
            for berth in range(1, 73):
                berth_type = 'LOWER' if berth % 8 in [1,4] else ('MIDDLE' if berth % 8 in [2,5] else 'UPPER')
                cursor.execute("""
                    INSERT INTO train_berths (coach_id, berth_number, berth_type)
                    VALUES (%s, %s, %s)
                """, (coach_id, str(berth), berth_type))
                berths_created += 1
        
        if train_id % 50 == 0:
            print(f"  Processed {train_id} trains...")
            conn.commit()
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"[OK] Created {coaches_created} coaches, {berths_created} berths")

if __name__ == "__main__":
    print("=" * 60)
    print("TRAIN DATA IMPORT")
    print("=" * 60)
    
    # Get paths to JSON files (one level up from backend folder)
    base_path = os.path.join(os.path.dirname(__file__), '..')
    
    # Import from all 3 JSON files
    import_trains_from_json(os.path.join(base_path, 'SF-TRAINS.json'), 'SUPERFAST')
    import_trains_from_json(os.path.join(base_path, 'EXP-TRAINS.json'), 'EXPRESS')
    import_trains_from_json(os.path.join(base_path, 'PASS-TRAINS.json'), 'PASSENGER')
    
    # Create coaches and berths
    create_sample_coaches()
    
    print("\n[OK] Train data import completed!")
