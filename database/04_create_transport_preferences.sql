-- Create Transport Preferences Table
-- Table to store detailed transport mode preferences for each search

USE transport_system;

DROP TABLE IF EXISTS transport_preferences;

CREATE TABLE transport_preferences (
    preference_id INT AUTO_INCREMENT PRIMARY KEY,
    search_id INT NOT NULL,
    user_id INT NOT NULL,
    -- Private mode preferences
    private_mode VARCHAR(50) NULL COMMENT 'bike, car, walk',
    -- Public mode preferences
    public_mode VARCHAR(50) NULL COMMENT 'bmtc, metro, aggregator',
    -- Multi-modal preferences
    multi_modal_type VARCHAR(50) NULL COMMENT 'luggage, elderly, child, family',
    -- Route optimization preference
    preference_type ENUM('cost', 'time', 'fuel') DEFAULT 'time',
    selected_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (search_id) REFERENCES route_searches(search_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_private_mode (private_mode),
    INDEX idx_public_mode (public_mode),
    INDEX idx_multi_modal (multi_modal_type),
    INDEX idx_preference_type (preference_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SELECT 'Transport preferences table created successfully!' AS Status;
