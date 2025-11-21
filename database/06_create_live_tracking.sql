-- Create Live Tracking Table
-- Table to store real-time tracking information for BMTC, Metro, and Aggregators

USE transport_system;

DROP TABLE IF EXISTS live_tracking;

CREATE TABLE live_tracking (
    tracking_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    user_id INT NOT NULL,
    vehicle_number VARCHAR(50) NULL,
    current_location VARCHAR(255) NULL,
    latitude DECIMAL(10, 8) NULL,
    longitude DECIMAL(11, 8) NULL,
    estimated_arrival TIME NULL,
    distance_remaining DECIMAL(10, 2) NULL COMMENT 'in kilometers',
    status ENUM('scheduled', 'in-transit', 'arrived', 'delayed', 'cancelled') DEFAULT 'scheduled',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_booking_tracking (booking_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SELECT 'Live tracking table created successfully!' AS Status;
