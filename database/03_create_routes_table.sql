-- Create Routes Search History Table
-- Table to store user route searches and preferences

USE transport_system;

DROP TABLE IF EXISTS route_searches;

CREATE TABLE route_searches (
    search_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    source_location VARCHAR(255) NOT NULL,
    destination_location VARCHAR(255) NOT NULL,
    transport_mode ENUM('private', 'public', 'multi-modal') NOT NULL,
    search_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_searches (user_id),
    INDEX idx_transport_mode (transport_mode),
    INDEX idx_timestamp (search_timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SELECT 'Route searches table created successfully!' AS Status;
