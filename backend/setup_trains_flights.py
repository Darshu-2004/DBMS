"""
Complete Train and Flight Booking Database Setup
"""
from database import execute_query

def create_train_tables():
    """Create all train-related tables"""
    
    # 1. Train Stations
    execute_query("""
        CREATE TABLE IF NOT EXISTS train_stations (
            station_id INT AUTO_INCREMENT PRIMARY KEY,
            station_name VARCHAR(100) NOT NULL,
            station_code VARCHAR(10) NOT NULL UNIQUE,
            city VARCHAR(100),
            state VARCHAR(50),
            latitude DECIMAL(10,8),
            longitude DECIMAL(11,8),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_station_code (station_code),
            INDEX idx_station_name (station_name)
        )
    """)
    
    # 2. Trains
    execute_query("""
        CREATE TABLE IF NOT EXISTS trains (
            train_id INT AUTO_INCREMENT PRIMARY KEY,
            train_number VARCHAR(10) NOT NULL UNIQUE,
            train_name VARCHAR(200) NOT NULL,
            train_type ENUM('SUPERFAST', 'EXPRESS', 'PASSENGER', 'RAJDHANI', 'SHATABDI') DEFAULT 'EXPRESS',
            source_station_code VARCHAR(10) NOT NULL,
            destination_station_code VARCHAR(10) NOT NULL,
            total_coaches INT DEFAULT 20,
            ac_1_coaches INT DEFAULT 2,
            ac_2_coaches INT DEFAULT 4,
            ac_3_coaches INT DEFAULT 6,
            sleeper_coaches INT DEFAULT 8,
            general_coaches INT DEFAULT 2,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_train_number (train_number),
            INDEX idx_train_type (train_type)
        )
    """)
    
    # 3. Train Schedules
    execute_query("""
        CREATE TABLE IF NOT EXISTS train_schedules (
            schedule_id INT AUTO_INCREMENT PRIMARY KEY,
            train_id INT NOT NULL,
            station_code VARCHAR(10) NOT NULL,
            arrival_time TIME,
            departure_time TIME,
            distance_km DECIMAL(10,2),
            day_number INT DEFAULT 1,
            stop_number INT NOT NULL,
            platform_number VARCHAR(5),
            FOREIGN KEY (train_id) REFERENCES trains(train_id) ON DELETE CASCADE,
            INDEX idx_train_station (train_id, station_code),
            INDEX idx_stop_number (train_id, stop_number)
        )
    """)
    
    # 4. Train Running Days
    execute_query("""
        CREATE TABLE IF NOT EXISTS train_running_days (
            id INT AUTO_INCREMENT PRIMARY KEY,
            train_id INT NOT NULL,
            sunday BOOLEAN DEFAULT FALSE,
            monday BOOLEAN DEFAULT FALSE,
            tuesday BOOLEAN DEFAULT FALSE,
            wednesday BOOLEAN DEFAULT FALSE,
            thursday BOOLEAN DEFAULT FALSE,
            friday BOOLEAN DEFAULT FALSE,
            saturday BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (train_id) REFERENCES trains(train_id) ON DELETE CASCADE,
            UNIQUE KEY unique_train_days (train_id)
        )
    """)
    
    # 5. Train Coaches (for seat mapping)
    execute_query("""
        CREATE TABLE IF NOT EXISTS train_coaches (
            coach_id INT AUTO_INCREMENT PRIMARY KEY,
            train_id INT NOT NULL,
            coach_number VARCHAR(10) NOT NULL,
            coach_type ENUM('AC-1', 'AC-2', 'AC-3', 'SLEEPER', 'GENERAL') NOT NULL,
            total_berths INT DEFAULT 72,
            FOREIGN KEY (train_id) REFERENCES trains(train_id) ON DELETE CASCADE,
            UNIQUE KEY unique_train_coach (train_id, coach_number),
            INDEX idx_coach_type (coach_type)
        )
    """)
    
    # 6. Train Berths/Seats
    execute_query("""
        CREATE TABLE IF NOT EXISTS train_berths (
            berth_id INT AUTO_INCREMENT PRIMARY KEY,
            coach_id INT NOT NULL,
            berth_number VARCHAR(10) NOT NULL,
            berth_type ENUM('LOWER', 'MIDDLE', 'UPPER', 'SIDE_LOWER', 'SIDE_UPPER') DEFAULT 'LOWER',
            is_available BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (coach_id) REFERENCES train_coaches(coach_id) ON DELETE CASCADE,
            UNIQUE KEY unique_coach_berth (coach_id, berth_number)
        )
    """)
    
    # 7. Train Bookings
    execute_query("""
        CREATE TABLE IF NOT EXISTS train_bookings (
            booking_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            train_id INT NOT NULL,
            pnr_number VARCHAR(20) UNIQUE NOT NULL,
            passenger_name VARCHAR(100) NOT NULL,
            passenger_age INT NOT NULL,
            passenger_gender ENUM('Male', 'Female', 'Other') NOT NULL,
            passenger_phone VARCHAR(15) NOT NULL,
            passenger_email VARCHAR(100),
            from_station VARCHAR(10) NOT NULL,
            to_station VARCHAR(10) NOT NULL,
            journey_date DATE NOT NULL,
            coach_type VARCHAR(20) NOT NULL,
            berth_numbers VARCHAR(200) NOT NULL,
            base_fare DECIMAL(10,2) NOT NULL,
            reservation_charges DECIMAL(10,2) DEFAULT 40.00,
            total_fare DECIMAL(10,2) NOT NULL,
            booking_status ENUM('Confirmed', 'RAC', 'Waitlisted', 'Cancelled') DEFAULT 'Confirmed',
            payment_status ENUM('Paid', 'Pending', 'Refunded') DEFAULT 'Paid',
            booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cancelled_at TIMESTAMP NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (train_id) REFERENCES trains(train_id) ON DELETE CASCADE,
            INDEX idx_pnr (pnr_number),
            INDEX idx_journey (journey_date, from_station, to_station),
            INDEX idx_user (user_id)
        )
    """)
    
    # 8. Train Tickets
    execute_query("""
        CREATE TABLE IF NOT EXISTS train_tickets (
            ticket_id INT AUTO_INCREMENT PRIMARY KEY,
            booking_id INT NOT NULL UNIQUE,
            ticket_number VARCHAR(30) UNIQUE NOT NULL,
            qr_code_data TEXT,
            chart_status ENUM('Not Prepared', 'Prepared') DEFAULT 'Not Prepared',
            is_expired BOOLEAN DEFAULT FALSE,
            expiry_datetime DATETIME,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES train_bookings(booking_id) ON DELETE CASCADE,
            INDEX idx_ticket_number (ticket_number)
        )
    """)
    
    # 9. Train User Expenses
    execute_query("""
        CREATE TABLE IF NOT EXISTS train_user_expenses (
            expense_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            booking_id INT NOT NULL,
            expense_date DATE NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            category VARCHAR(50) DEFAULT 'Train Ticket',
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (booking_id) REFERENCES train_bookings(booking_id) ON DELETE CASCADE,
            INDEX idx_user_date (user_id, expense_date)
        )
    """)
    
    print("[OK] Train tables created successfully!")

def create_flight_tables():
    """Create all flight-related tables"""
    
    # 1. Airports
    execute_query("""
        CREATE TABLE IF NOT EXISTS airports (
            airport_id INT AUTO_INCREMENT PRIMARY KEY,
            airport_code VARCHAR(10) NOT NULL UNIQUE,
            airport_name VARCHAR(200) NOT NULL,
            city VARCHAR(100) NOT NULL,
            country VARCHAR(100) DEFAULT 'India',
            latitude DECIMAL(10,8),
            longitude DECIMAL(11,8),
            timezone VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_airport_code (airport_code),
            INDEX idx_city (city)
        )
    """)
    
    # 2. Airlines
    execute_query("""
        CREATE TABLE IF NOT EXISTS airlines (
            airline_id INT AUTO_INCREMENT PRIMARY KEY,
            airline_name VARCHAR(100) NOT NULL UNIQUE,
            airline_code VARCHAR(10) NOT NULL UNIQUE,
            country VARCHAR(50) DEFAULT 'India',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_airline_code (airline_code)
        )
    """)
    
    # 3. Flights
    execute_query("""
        CREATE TABLE IF NOT EXISTS flights (
            flight_id INT AUTO_INCREMENT PRIMARY KEY,
            airline_id INT NOT NULL,
            flight_number VARCHAR(20) NOT NULL,
            origin_code VARCHAR(10) NOT NULL,
            destination_code VARCHAR(10) NOT NULL,
            departure_time TIME NOT NULL,
            arrival_time TIME,
            flight_duration_mins INT,
            aircraft_type VARCHAR(50),
            economy_seats INT DEFAULT 150,
            business_seats INT DEFAULT 20,
            total_seats INT DEFAULT 170,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (airline_id) REFERENCES airlines(airline_id) ON DELETE CASCADE,
            INDEX idx_flight_number (flight_number),
            INDEX idx_route (origin_code, destination_code)
        )
    """)
    
    # 4. Flight Schedules (Days of operation)
    execute_query("""
        CREATE TABLE IF NOT EXISTS flight_schedules (
            schedule_id INT AUTO_INCREMENT PRIMARY KEY,
            flight_id INT NOT NULL,
            sunday BOOLEAN DEFAULT FALSE,
            monday BOOLEAN DEFAULT FALSE,
            tuesday BOOLEAN DEFAULT FALSE,
            wednesday BOOLEAN DEFAULT FALSE,
            thursday BOOLEAN DEFAULT FALSE,
            friday BOOLEAN DEFAULT FALSE,
            saturday BOOLEAN DEFAULT FALSE,
            valid_from DATE,
            valid_to DATE,
            FOREIGN KEY (flight_id) REFERENCES flights(flight_id) ON DELETE CASCADE,
            INDEX idx_flight (flight_id)
        )
    """)
    
    # 5. Flight Seats
    execute_query("""
        CREATE TABLE IF NOT EXISTS flight_seats (
            seat_id INT AUTO_INCREMENT PRIMARY KEY,
            flight_id INT NOT NULL,
            seat_number VARCHAR(10) NOT NULL,
            seat_class ENUM('Economy', 'Business', 'First Class') DEFAULT 'Economy',
            seat_row INT,
            seat_column VARCHAR(5),
            is_window BOOLEAN DEFAULT FALSE,
            is_aisle BOOLEAN DEFAULT FALSE,
            is_available BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (flight_id) REFERENCES flights(flight_id) ON DELETE CASCADE,
            UNIQUE KEY unique_flight_seat (flight_id, seat_number),
            INDEX idx_class (seat_class)
        )
    """)
    
    # 6. Flight Bookings
    execute_query("""
        CREATE TABLE IF NOT EXISTS flight_bookings (
            booking_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            flight_id INT NOT NULL,
            booking_reference VARCHAR(10) UNIQUE NOT NULL,
            passenger_name VARCHAR(100) NOT NULL,
            passenger_age INT NOT NULL,
            passenger_gender ENUM('Male', 'Female', 'Other') NOT NULL,
            passenger_phone VARCHAR(15) NOT NULL,
            passenger_email VARCHAR(100),
            from_airport VARCHAR(10) NOT NULL,
            to_airport VARCHAR(10) NOT NULL,
            journey_date DATE NOT NULL,
            seat_class VARCHAR(20) NOT NULL,
            seat_numbers VARCHAR(200) NOT NULL,
            base_fare DECIMAL(10,2) NOT NULL,
            taxes_fees DECIMAL(10,2) DEFAULT 500.00,
            total_fare DECIMAL(10,2) NOT NULL,
            booking_status ENUM('Confirmed', 'Cancelled', 'Completed') DEFAULT 'Confirmed',
            payment_status ENUM('Paid', 'Pending', 'Refunded') DEFAULT 'Paid',
            checkin_status ENUM('Not Checked In', 'Checked In') DEFAULT 'Not Checked In',
            booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cancelled_at TIMESTAMP NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (flight_id) REFERENCES flights(flight_id) ON DELETE CASCADE,
            INDEX idx_booking_ref (booking_reference),
            INDEX idx_journey (journey_date, from_airport, to_airport),
            INDEX idx_user (user_id)
        )
    """)
    
    # 7. Boarding Passes
    execute_query("""
        CREATE TABLE IF NOT EXISTS boarding_passes (
            pass_id INT AUTO_INCREMENT PRIMARY KEY,
            booking_id INT NOT NULL UNIQUE,
            boarding_pass_number VARCHAR(30) UNIQUE NOT NULL,
            barcode_data TEXT,
            gate_number VARCHAR(10),
            boarding_time TIME,
            is_expired BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES flight_bookings(booking_id) ON DELETE CASCADE,
            INDEX idx_pass_number (boarding_pass_number)
        )
    """)
    
    # 8. Flight User Expenses
    execute_query("""
        CREATE TABLE IF NOT EXISTS flight_user_expenses (
            expense_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            booking_id INT NOT NULL,
            expense_date DATE NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            category VARCHAR(50) DEFAULT 'Flight Ticket',
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (booking_id) REFERENCES flight_bookings(booking_id) ON DELETE CASCADE,
            INDEX idx_user_date (user_id, expense_date)
        )
    """)
    
    print("[OK] Flight tables created successfully!")

if __name__ == "__main__":
    print("Creating train tables...")
    create_train_tables()
    print("\nCreating flight tables...")
    create_flight_tables()
    print("\n[OK] All tables created successfully!")
