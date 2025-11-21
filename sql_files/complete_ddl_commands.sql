-- ============================================================
-- COMPLETE DDL COMMANDS
-- Multi-Modal Transport System Database
-- All CREATE TABLE statements
-- ============================================================

-- Database Creation
DROP DATABASE IF EXISTS transport_system;
CREATE DATABASE transport_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE transport_system;

-- ============================================================
-- 1. USERS TABLE
-- ============================================================
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    user_type ENUM('user', 'admin') DEFAULT 'user',
    INDEX idx_email (email),
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 2. KSRTC TABLES
-- ============================================================

-- KSRTC Routes
DROP TABLE IF EXISTS ksrtc_routes;
CREATE TABLE ksrtc_routes (
    route_id INT AUTO_INCREMENT PRIMARY KEY,
    route_name VARCHAR(100) NOT NULL,
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    distance_km DECIMAL(6,2) NOT NULL,
    estimated_duration INT NOT NULL COMMENT 'Duration in minutes',
    base_fare DECIMAL(8,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_route_origin (origin),
    INDEX idx_route_destination (destination)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- KSRTC Buses
DROP TABLE IF EXISTS ksrtc_buses;
CREATE TABLE ksrtc_buses (
    bus_id INT AUTO_INCREMENT PRIMARY KEY,
    bus_number VARCHAR(20) NOT NULL UNIQUE,
    bus_type ENUM('Ordinary', 'Express', 'Airavat', 'Airavat Club Class') NOT NULL,
    total_seats INT NOT NULL,
    facilities TEXT,
    registration_number VARCHAR(20) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_bus_type (bus_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- KSRTC Schedules
DROP TABLE IF EXISTS ksrtc_schedules;
CREATE TABLE ksrtc_schedules (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    route_id INT NOT NULL,
    bus_id INT NOT NULL,
    departure_time TIME NOT NULL,
    arrival_time TIME NOT NULL,
    operating_days VARCHAR(50) NOT NULL COMMENT 'Days when bus operates',
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (route_id) REFERENCES ksrtc_routes(route_id),
    FOREIGN KEY (bus_id) REFERENCES ksrtc_buses(bus_id),
    INDEX idx_departure_time (departure_time),
    INDEX idx_route_schedule (route_id, departure_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- KSRTC Seats
DROP TABLE IF EXISTS ksrtc_seats;
CREATE TABLE ksrtc_seats (
    seat_id INT AUTO_INCREMENT PRIMARY KEY,
    bus_id INT NOT NULL,
    seat_number VARCHAR(5) NOT NULL,
    seat_type ENUM('Window', 'Aisle', 'Middle') NOT NULL,
    is_sleeper BOOLEAN DEFAULT FALSE,
    is_available BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (bus_id) REFERENCES ksrtc_buses(bus_id),
    UNIQUE KEY unique_bus_seat (bus_id, seat_number),
    INDEX idx_bus_availability (bus_id, is_available)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- KSRTC Bookings
DROP TABLE IF EXISTS ksrtc_bookings;
CREATE TABLE ksrtc_bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    schedule_id INT NOT NULL,
    booking_reference VARCHAR(50) UNIQUE NOT NULL,
    journey_date DATE NOT NULL,
    passenger_name VARCHAR(100) NOT NULL,
    passenger_age INT NOT NULL,
    passenger_gender ENUM('Male', 'Female', 'Other') NOT NULL,
    seat_numbers VARCHAR(100) NOT NULL,
    total_fare DECIMAL(10,2) NOT NULL,
    booking_status ENUM('Confirmed', 'Cancelled') DEFAULT 'Confirmed',
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (schedule_id) REFERENCES ksrtc_schedules(schedule_id),
    INDEX idx_user_bookings (user_id),
    INDEX idx_journey_date (journey_date),
    INDEX idx_booking_status (booking_status),
    INDEX idx_booking_ref (booking_reference)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- KSRTC Tickets
DROP TABLE IF EXISTS ksrtc_tickets;
CREATE TABLE ksrtc_tickets (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    ticket_number VARCHAR(50) UNIQUE NOT NULL,
    qr_code TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES ksrtc_bookings(booking_id) ON DELETE CASCADE,
    INDEX idx_ticket_number (ticket_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 3. TRAIN TABLES
-- ============================================================

-- Trains
DROP TABLE IF EXISTS trains;
CREATE TABLE trains (
    train_id INT AUTO_INCREMENT PRIMARY KEY,
    train_number VARCHAR(10) NOT NULL UNIQUE,
    train_name VARCHAR(100) NOT NULL,
    train_type ENUM('Express', 'Superfast', 'Passenger', 'Duronto', 'Rajdhani', 'Shatabdi') NOT NULL,
    total_coaches INT NOT NULL,
    INDEX idx_train_number (train_number),
    INDEX idx_train_type (train_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Train Stations
DROP TABLE IF EXISTS train_stations;
CREATE TABLE train_stations (
    station_id INT AUTO_INCREMENT PRIMARY KEY,
    station_code VARCHAR(10) NOT NULL UNIQUE,
    station_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL,
    INDEX idx_station_code (station_code),
    INDEX idx_city (city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Train Schedules
DROP TABLE IF EXISTS train_schedules;
CREATE TABLE train_schedules (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    train_id INT NOT NULL,
    station_code VARCHAR(10) NOT NULL,
    arrival_time TIME NULL,
    departure_time TIME NULL,
    stop_number INT NOT NULL,
    platform_number VARCHAR(5),
    distance_km DECIMAL(8,2) NOT NULL DEFAULT 0,
    FOREIGN KEY (train_id) REFERENCES trains(train_id),
    FOREIGN KEY (station_code) REFERENCES train_stations(station_code),
    INDEX idx_train_schedule (train_id, stop_number),
    INDEX idx_station_schedule (station_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Train Running Days
DROP TABLE IF EXISTS train_running_days;
CREATE TABLE train_running_days (
    id INT AUTO_INCREMENT PRIMARY KEY,
    train_id INT NOT NULL,
    runs_on_monday BOOLEAN DEFAULT FALSE,
    runs_on_tuesday BOOLEAN DEFAULT FALSE,
    runs_on_wednesday BOOLEAN DEFAULT FALSE,
    runs_on_thursday BOOLEAN DEFAULT FALSE,
    runs_on_friday BOOLEAN DEFAULT FALSE,
    runs_on_saturday BOOLEAN DEFAULT FALSE,
    runs_on_sunday BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (train_id) REFERENCES trains(train_id),
    UNIQUE KEY unique_train_days (train_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Train Coaches
DROP TABLE IF EXISTS train_coaches;
CREATE TABLE train_coaches (
    coach_id INT AUTO_INCREMENT PRIMARY KEY,
    train_id INT NOT NULL,
    coach_type VARCHAR(10) NOT NULL COMMENT 'SL, 2A, 3A, CC, EC, etc.',
    coach_count INT NOT NULL,
    seats_per_coach INT NOT NULL,
    base_fare DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (train_id) REFERENCES trains(train_id),
    INDEX idx_train_coach_type (train_id, coach_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Train Bookings
DROP TABLE IF EXISTS train_bookings;
CREATE TABLE train_bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    train_id INT NOT NULL,
    pnr_number VARCHAR(10) UNIQUE NOT NULL,
    journey_date DATE NOT NULL,
    source_station VARCHAR(10) NOT NULL,
    destination_station VARCHAR(10) NOT NULL,
    coach_type VARCHAR(10) NOT NULL,
    seat_count INT NOT NULL,
    berth_preference VARCHAR(20),
    passenger_names TEXT NOT NULL,
    berth_numbers VARCHAR(200),
    total_fare DECIMAL(10,2) NOT NULL,
    booking_status ENUM('Confirmed', 'Cancelled', 'Waitlisted') DEFAULT 'Confirmed',
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (train_id) REFERENCES trains(train_id),
    INDEX idx_user_bookings (user_id),
    INDEX idx_pnr (pnr_number),
    INDEX idx_journey_date (journey_date),
    INDEX idx_booking_status (booking_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 4. FLIGHT TABLES
-- ============================================================

-- Airlines
DROP TABLE IF EXISTS airlines;
CREATE TABLE airlines (
    airline_id INT AUTO_INCREMENT PRIMARY KEY,
    airline_code VARCHAR(5) NOT NULL UNIQUE,
    airline_name VARCHAR(100) NOT NULL,
    country VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_airline_code (airline_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Airports
DROP TABLE IF EXISTS airports;
CREATE TABLE airports (
    airport_id INT AUTO_INCREMENT PRIMARY KEY,
    airport_code VARCHAR(5) NOT NULL UNIQUE,
    airport_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    INDEX idx_airport_code (airport_code),
    INDEX idx_city (city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Flights
DROP TABLE IF EXISTS flights;
CREATE TABLE flights (
    flight_id INT AUTO_INCREMENT PRIMARY KEY,
    airline_id INT NOT NULL,
    flight_number VARCHAR(10) NOT NULL,
    origin_code VARCHAR(5) NOT NULL,
    destination_code VARCHAR(5) NOT NULL,
    aircraft_type VARCHAR(50) NOT NULL,
    total_seats INT NOT NULL,
    FOREIGN KEY (airline_id) REFERENCES airlines(airline_id),
    FOREIGN KEY (origin_code) REFERENCES airports(airport_code),
    FOREIGN KEY (destination_code) REFERENCES airports(airport_code),
    INDEX idx_flight_number (flight_number),
    INDEX idx_route (origin_code, destination_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Flight Schedules
DROP TABLE IF EXISTS flight_schedules;
CREATE TABLE flight_schedules (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    flight_id INT NOT NULL,
    departure_time TIME NOT NULL,
    arrival_time TIME NOT NULL,
    duration_minutes INT NOT NULL,
    operates_on VARCHAR(50) NOT NULL COMMENT 'Days of week',
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (flight_id) REFERENCES flights(flight_id),
    INDEX idx_flight_schedule (flight_id, departure_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Flight Seats
DROP TABLE IF EXISTS flight_seats;
CREATE TABLE flight_seats (
    seat_id INT AUTO_INCREMENT PRIMARY KEY,
    flight_id INT NOT NULL,
    seat_number VARCHAR(5) NOT NULL,
    class_type ENUM('Economy', 'Business', 'First') NOT NULL,
    base_fare DECIMAL(10,2) NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (flight_id) REFERENCES flights(flight_id),
    UNIQUE KEY unique_flight_seat (flight_id, seat_number),
    INDEX idx_flight_class (flight_id, class_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Flight Bookings
DROP TABLE IF EXISTS flight_bookings;
CREATE TABLE flight_bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    flight_id INT NOT NULL,
    booking_reference VARCHAR(50) UNIQUE NOT NULL,
    journey_date DATE NOT NULL,
    passenger_names TEXT NOT NULL,
    seat_numbers VARCHAR(200),
    class_type ENUM('Economy', 'Business', 'First') NOT NULL,
    total_fare DECIMAL(10,2) NOT NULL,
    booking_status ENUM('Confirmed', 'Cancelled') DEFAULT 'Confirmed',
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (flight_id) REFERENCES flights(flight_id),
    INDEX idx_user_bookings (user_id),
    INDEX idx_booking_ref (booking_reference),
    INDEX idx_journey_date (journey_date),
    INDEX idx_booking_status (booking_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- 5. TRIGGER SUPPORT TABLE
-- ============================================================

DROP TABLE IF EXISTS booking_activity_log;
CREATE TABLE booking_activity_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_type VARCHAR(20) NOT NULL,
    booking_reference VARCHAR(50) NOT NULL,
    user_id INT NOT NULL,
    action_type ENUM('INSERT', 'UPDATE') NOT NULL,
    old_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    total_fare DECIMAL(10,2) NOT NULL,
    journey_date DATE NOT NULL,
    log_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_booking_type (booking_type),
    INDEX idx_action_type (action_type),
    INDEX idx_log_timestamp (log_timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================
-- END OF DDL COMMANDS
-- ============================================================

SELECT 'All tables created successfully!' AS Status;
