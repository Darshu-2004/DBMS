-- Create Bookings Table
-- Table to store all transport bookings (BMTC, Metro, Aggregators, KSRTC, Buses, Trains, Flights)

USE transport_system;

DROP TABLE IF EXISTS bookings;

CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    booking_type ENUM('bmtc', 'metro', 'aggregator', 'ksrtc', 'private_bus', 'train', 'flight', 'parcel') NOT NULL,
    source VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    booking_date DATE NOT NULL,
    booking_time TIME NULL,
    journey_date DATE NOT NULL,
    journey_time TIME NULL,
    passenger_count INT DEFAULT 1,
    fare_amount DECIMAL(10, 2) NULL,
    booking_status ENUM('pending', 'confirmed', 'cancelled', 'completed') DEFAULT 'pending',
    booking_reference VARCHAR(100) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_bookings (user_id),
    INDEX idx_booking_type (booking_type),
    INDEX idx_journey_date (journey_date),
    INDEX idx_booking_status (booking_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SELECT 'Bookings table created successfully!' AS Status;
