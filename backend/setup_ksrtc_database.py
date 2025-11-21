"""
KSRTC Database Setup Script
Creates all necessary tables for KSRTC bus booking system
"""

from database import execute_query

def create_ksrtc_tables():
    """Create all KSRTC related tables"""
    
    # 1. KSRTC Routes table
    execute_query("""
        CREATE TABLE IF NOT EXISTS ksrtc_routes (
            route_id INT AUTO_INCREMENT PRIMARY KEY,
            route_number VARCHAR(20) UNIQUE NOT NULL,
            source VARCHAR(100) NOT NULL,
            destination VARCHAR(100) NOT NULL,
            distance_km DECIMAL(10,2),
            estimated_duration_mins INT,
            via_places TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_source (source),
            INDEX idx_destination (destination),
            INDEX idx_route_number (route_number)
        )
    """)
    
    # 2. KSRTC Stops table
    execute_query("""
        CREATE TABLE IF NOT EXISTS ksrtc_stops (
            stop_id INT AUTO_INCREMENT PRIMARY KEY,
            stop_name VARCHAR(100) UNIQUE NOT NULL,
            city VARCHAR(50),
            district VARCHAR(50),
            latitude DECIMAL(10,8),
            longitude DECIMAL(11,8),
            is_major_stop BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_stop_name (stop_name),
            INDEX idx_city (city)
        )
    """)
    
    # 3. KSRTC Buses table
    execute_query("""
        CREATE TABLE IF NOT EXISTS ksrtc_buses (
            bus_id INT AUTO_INCREMENT PRIMARY KEY,
            bus_number VARCHAR(20) UNIQUE NOT NULL,
            bus_type ENUM('K/S', 'VOLVO', 'NON A/C SLEEPER', 'PALLAKKI', 'ASHWAMEDHA', 'R/H', 'EV') NOT NULL,
            total_seats INT DEFAULT 40,
            seater_seats INT DEFAULT 40,
            sleeper_seats INT DEFAULT 0,
            ac_available BOOLEAN DEFAULT FALSE,
            amenities TEXT,
            registration_number VARCHAR(20),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_bus_type (bus_type)
        )
    """)
    
    # 4. KSRTC Schedules table
    execute_query("""
        CREATE TABLE IF NOT EXISTS ksrtc_schedules (
            schedule_id INT AUTO_INCREMENT PRIMARY KEY,
            route_id INT NOT NULL,
            bus_id INT NOT NULL,
            departure_time TIME NOT NULL,
            arrival_time TIME,
            service_days VARCHAR(50) DEFAULT 'Daily',
            base_fare DECIMAL(10,2) NOT NULL,
            status ENUM('Active', 'Cancelled', 'Delayed') DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (route_id) REFERENCES ksrtc_routes(route_id) ON DELETE CASCADE,
            FOREIGN KEY (bus_id) REFERENCES ksrtc_buses(bus_id) ON DELETE CASCADE,
            INDEX idx_departure_time (departure_time),
            INDEX idx_route_bus (route_id, bus_id)
        )
    """)
    
    # 5. KSRTC Seats table
    execute_query("""
        CREATE TABLE IF NOT EXISTS ksrtc_seats (
            seat_id INT AUTO_INCREMENT PRIMARY KEY,
            bus_id INT NOT NULL,
            seat_number VARCHAR(10) NOT NULL,
            seat_type ENUM('Seater', 'Sleeper', 'Window', 'Aisle') DEFAULT 'Seater',
            deck ENUM('Lower', 'Upper') DEFAULT 'Lower',
            seat_row INT,
            seat_column VARCHAR(5),
            is_available BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (bus_id) REFERENCES ksrtc_buses(bus_id) ON DELETE CASCADE,
            UNIQUE KEY unique_bus_seat (bus_id, seat_number),
            INDEX idx_bus_seat (bus_id, is_available)
        )
    """)
    
    # 6. KSRTC Bookings table
    execute_query("""
        CREATE TABLE IF NOT EXISTS ksrtc_bookings (
            booking_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            schedule_id INT NOT NULL,
            booking_reference VARCHAR(20) UNIQUE NOT NULL,
            passenger_name VARCHAR(100) NOT NULL,
            passenger_age INT,
            passenger_gender ENUM('Male', 'Female', 'Other'),
            passenger_phone VARCHAR(15) NOT NULL,
            passenger_email VARCHAR(100),
            boarding_stop VARCHAR(100) NOT NULL,
            destination_stop VARCHAR(100) NOT NULL,
            journey_date DATE NOT NULL,
            seat_numbers VARCHAR(100) NOT NULL,
            total_fare DECIMAL(10,2) NOT NULL,
            booking_status ENUM('Confirmed', 'Cancelled', 'Completed', 'No Show') DEFAULT 'Confirmed',
            payment_status ENUM('Pending', 'Paid', 'Refunded') DEFAULT 'Paid',
            payment_method VARCHAR(50),
            booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cancelled_at TIMESTAMP NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (schedule_id) REFERENCES ksrtc_schedules(schedule_id) ON DELETE CASCADE,
            INDEX idx_user_bookings (user_id),
            INDEX idx_journey_date (journey_date),
            INDEX idx_booking_ref (booking_reference),
            INDEX idx_status (booking_status)
        )
    """)
    
    # 7. KSRTC Tickets table (for QR codes and mobile tickets)
    execute_query("""
        CREATE TABLE IF NOT EXISTS ksrtc_tickets (
            ticket_id INT AUTO_INCREMENT PRIMARY KEY,
            booking_id INT NOT NULL UNIQUE,
            ticket_number VARCHAR(30) UNIQUE NOT NULL,
            qr_code_data TEXT,
            qr_code_path VARCHAR(255),
            is_expired BOOLEAN DEFAULT FALSE,
            validated_at TIMESTAMP NULL,
            expiry_datetime DATETIME,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES ksrtc_bookings(booking_id) ON DELETE CASCADE,
            INDEX idx_ticket_number (ticket_number),
            INDEX idx_expiry (expiry_datetime, is_expired)
        )
    """)
    
    # 8. KSRTC Seat Locks table (to prevent double booking during payment)
    execute_query("""
        CREATE TABLE IF NOT EXISTS ksrtc_seat_locks (
            lock_id INT AUTO_INCREMENT PRIMARY KEY,
            schedule_id INT NOT NULL,
            journey_date DATE NOT NULL,
            seat_number VARCHAR(10) NOT NULL,
            locked_by_user INT NOT NULL,
            locked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            is_booked BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (schedule_id) REFERENCES ksrtc_schedules(schedule_id) ON DELETE CASCADE,
            FOREIGN KEY (locked_by_user) REFERENCES users(user_id) ON DELETE CASCADE,
            UNIQUE KEY unique_seat_lock (schedule_id, journey_date, seat_number),
            INDEX idx_expiry (expires_at, is_booked)
        )
    """)
    
    # 9. KSRTC User Expenses table (for tracking spending)
    execute_query("""
        CREATE TABLE IF NOT EXISTS ksrtc_user_expenses (
            expense_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            booking_id INT NOT NULL,
            expense_date DATE NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            category VARCHAR(50) DEFAULT 'Bus Ticket',
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (booking_id) REFERENCES ksrtc_bookings(booking_id) ON DELETE CASCADE,
            INDEX idx_user_date (user_id, expense_date),
            INDEX idx_expense_date (expense_date)
        )
    """)
    
    # 10. KSRTC Route Stops junction table
    execute_query("""
        CREATE TABLE IF NOT EXISTS ksrtc_route_stops (
            id INT AUTO_INCREMENT PRIMARY KEY,
            route_id INT NOT NULL,
            stop_id INT NOT NULL,
            stop_sequence INT NOT NULL,
            arrival_time_offset_mins INT DEFAULT 0,
            fare_from_source DECIMAL(10,2),
            distance_from_source_km DECIMAL(10,2),
            FOREIGN KEY (route_id) REFERENCES ksrtc_routes(route_id) ON DELETE CASCADE,
            FOREIGN KEY (stop_id) REFERENCES ksrtc_stops(stop_id) ON DELETE CASCADE,
            UNIQUE KEY unique_route_stop (route_id, stop_id),
            INDEX idx_route_sequence (route_id, stop_sequence)
        )
    """)
    
    print("✓ All KSRTC tables created successfully!")

if __name__ == "__main__":
    create_ksrtc_tables()
