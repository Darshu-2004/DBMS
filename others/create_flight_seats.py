import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Darshu@2004",
    database="transport_system"
)
cursor = conn.cursor()

print("Creating flight seats...")

# Get all flights
cursor.execute("SELECT flight_id FROM flights")
flights = cursor.fetchall()

seat_count = 0
for flight_row in flights:
    flight_id = flight_row[0]
    
    # Economy seats: 150 seats (Rows 1-25, columns A-F)
    for row in range(1, 26):
        for col in ['A', 'B', 'C', 'D', 'E', 'F']:
            seat_number = f"{row}{col}"
            is_window = col in ['A', 'F']
            is_aisle = col in ['C', 'D']
            
            cursor.execute("""
                INSERT INTO flight_seats (flight_id, seat_number, seat_class, seat_row, seat_column, 
                                         is_window, is_aisle, is_available)
                VALUES (%s, %s, 'Economy', %s, %s, %s, %s, TRUE)
            """, (flight_id, seat_number, row, col, is_window, is_aisle))
            seat_count += 1
    
    # Business seats: 12 seats (Rows 26-27, columns A-F)
    for row in range(26, 28):
        for col in ['A', 'B', 'C', 'D', 'E', 'F']:
            seat_number = f"{row}{col}"
            is_window = col in ['A', 'F']
            is_aisle = col in ['C', 'D']
            
            cursor.execute("""
                INSERT INTO flight_seats (flight_id, seat_number, seat_class, seat_row, seat_column, 
                                         is_window, is_aisle, is_available)
                VALUES (%s, %s, 'Business', %s, %s, %s, %s, TRUE)
            """, (flight_id, seat_number, row, col, is_window, is_aisle))
            seat_count += 1
    
    if flight_id % 50 == 0:
        print(f"  Created seats for {flight_id} flights...")
        conn.commit()

conn.commit()
print(f"\n✅ Created {seat_count} seats for {len(flights)} flights!")
print(f"   Economy: 150 seats per flight")
print(f"   Business: 12 seats per flight")

cursor.close()
conn.close()
