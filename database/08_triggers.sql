-- Database Triggers for Booking Activity Logging
-- Created: November 20, 2025
-- Purpose: Demonstrate trigger usage without affecting existing functionality

USE transport_system;

-- Create a simple log table for trigger demonstration
DROP TABLE IF EXISTS booking_activity_log;

CREATE TABLE booking_activity_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_type ENUM('KSRTC', 'Train', 'Flight') NOT NULL,
    booking_reference VARCHAR(100),
    user_id INT,
    action_type ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    total_fare DECIMAL(10, 2),
    journey_date DATE,
    log_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_booking_type (booking_type),
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (log_timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Drop existing triggers if they exist
DROP TRIGGER IF EXISTS after_ksrtc_booking_insert;
DROP TRIGGER IF EXISTS after_train_booking_insert;
DROP TRIGGER IF EXISTS after_flight_booking_insert;
DROP TRIGGER IF EXISTS after_ksrtc_booking_update;
DROP TRIGGER IF EXISTS after_train_booking_update;
DROP TRIGGER IF EXISTS after_flight_booking_update;

-- ============================================
-- KSRTC BOOKING TRIGGERS
-- ============================================

-- Trigger: Log new KSRTC bookings
DELIMITER //
CREATE TRIGGER after_ksrtc_booking_insert
AFTER INSERT ON ksrtc_bookings
FOR EACH ROW
BEGIN
    INSERT INTO booking_activity_log (
        booking_type, booking_reference, user_id, action_type, 
        old_status, new_status, total_fare, journey_date
    ) VALUES (
        'KSRTC', NEW.booking_reference, NEW.user_id, 'INSERT',
        NULL, NEW.booking_status, NEW.total_fare, NEW.journey_date
    );
END//
DELIMITER ;

-- Trigger: Log KSRTC booking updates
DELIMITER //
CREATE TRIGGER after_ksrtc_booking_update
AFTER UPDATE ON ksrtc_bookings
FOR EACH ROW
BEGIN
    INSERT INTO booking_activity_log (
        booking_type, booking_reference, user_id, action_type,
        old_status, new_status, total_fare, journey_date
    ) VALUES (
        'KSRTC', NEW.booking_reference, NEW.user_id, 'UPDATE',
        OLD.booking_status, NEW.booking_status, NEW.total_fare, NEW.journey_date
    );
END//
DELIMITER ;

-- ============================================
-- TRAIN BOOKING TRIGGERS
-- ============================================

-- Trigger: Log new train bookings
DELIMITER //
CREATE TRIGGER after_train_booking_insert
AFTER INSERT ON train_bookings
FOR EACH ROW
BEGIN
    INSERT INTO booking_activity_log (
        booking_type, booking_reference, user_id, action_type,
        old_status, new_status, total_fare, journey_date
    ) VALUES (
        'Train', NEW.pnr_number, NEW.user_id, 'INSERT',
        NULL, NEW.booking_status, NEW.total_fare, NEW.journey_date
    );
END//
DELIMITER ;

-- Trigger: Log train booking updates
DELIMITER //
CREATE TRIGGER after_train_booking_update
AFTER UPDATE ON train_bookings
FOR EACH ROW
BEGIN
    INSERT INTO booking_activity_log (
        booking_type, booking_reference, user_id, action_type,
        old_status, new_status, total_fare, journey_date
    ) VALUES (
        'Train', NEW.pnr_number, NEW.user_id, 'UPDATE',
        OLD.booking_status, NEW.booking_status, NEW.total_fare, NEW.journey_date
    );
END//
DELIMITER ;

-- ============================================
-- FLIGHT BOOKING TRIGGERS
-- ============================================

-- Trigger: Log new flight bookings
DELIMITER //
CREATE TRIGGER after_flight_booking_insert
AFTER INSERT ON flight_bookings
FOR EACH ROW
BEGIN
    INSERT INTO booking_activity_log (
        booking_type, booking_reference, user_id, action_type,
        old_status, new_status, total_fare, journey_date
    ) VALUES (
        'Flight', NEW.booking_reference, NEW.user_id, 'INSERT',
        NULL, NEW.booking_status, NEW.total_fare, NEW.journey_date
    );
END//
DELIMITER ;

-- Trigger: Log flight booking updates
DELIMITER //
CREATE TRIGGER after_flight_booking_update
AFTER UPDATE ON flight_bookings
FOR EACH ROW
BEGIN
    INSERT INTO booking_activity_log (
        booking_type, booking_reference, user_id, action_type,
        old_status, new_status, total_fare, journey_date
    ) VALUES (
        'Flight', NEW.booking_reference, NEW.user_id, 'UPDATE',
        OLD.booking_status, NEW.booking_status, NEW.total_fare, NEW.journey_date
    );
END//
DELIMITER ;

-- ============================================
-- VERIFICATION
-- ============================================

SELECT 'Triggers created successfully!' AS Status;

-- Show all triggers
SHOW TRIGGERS WHERE `Table` IN ('ksrtc_bookings', 'train_bookings', 'flight_bookings');

            NEW.total_fare,
            CONCAT('KSRTC Booking: ', NEW.boarding_stop, ' to ', NEW.destination_stop, ' (Ref: ', NEW.booking_reference, ')'),
            NEW.journey_date,
            NOW()
        );
    END IF;
    
    -- If booking was cancelled, remove or mark expense
    IF OLD.booking_status = 'Confirmed' AND NEW.booking_status = 'Cancelled' THEN
        DELETE FROM expenses 
        WHERE user_id = NEW.user_id 
        AND category = 'KSRTC' 
        AND description LIKE CONCAT('%Ref: ', NEW.booking_reference, '%')
        LIMIT 1;
    END IF;
END//
DELIMITER ;

-- ============================================
-- TRAIN BOOKING TRIGGERS
-- ============================================

-- Trigger: Auto-insert expense when Train booking is created
DELIMITER //
CREATE TRIGGER after_train_booking_insert
AFTER INSERT ON train_bookings
FOR EACH ROW
BEGIN
    -- Insert into expenses table when booking is confirmed
    IF NEW.booking_status = 'Confirmed' THEN
        INSERT INTO expenses (user_id, category, amount, description, expense_date, created_at)
        VALUES (
            NEW.user_id,
            'Train Ticket',
            NEW.total_fare,
            CONCAT('Train Booking: ', NEW.from_station, ' to ', NEW.to_station, ' (PNR: ', NEW.pnr_number, ')'),
            NEW.journey_date,
            NOW()
        );
    END IF;
END//
DELIMITER ;

-- Trigger: Update expense when Train booking status changes
DELIMITER //
CREATE TRIGGER after_train_booking_update
AFTER UPDATE ON train_bookings
FOR EACH ROW
BEGIN
    -- If booking was just confirmed, add expense
    IF OLD.booking_status != 'Confirmed' AND NEW.booking_status = 'Confirmed' THEN
        INSERT INTO expenses (user_id, category, amount, description, expense_date, created_at)
        VALUES (
            NEW.user_id,
            'Train Ticket',
            NEW.total_fare,
            CONCAT('Train Booking: ', NEW.from_station, ' to ', NEW.to_station, ' (PNR: ', NEW.pnr_number, ')'),
            NEW.journey_date,
            NOW()
        );
    END IF;
    
    -- If booking was cancelled, remove expense
    IF OLD.booking_status = 'Confirmed' AND NEW.booking_status = 'Cancelled' THEN
        DELETE FROM expenses 
        WHERE user_id = NEW.user_id 
        AND category = 'Train Ticket' 
        AND description LIKE CONCAT('%PNR: ', NEW.pnr_number, '%')
        LIMIT 1;
    END IF;
END//
DELIMITER ;

-- ============================================
-- FLIGHT BOOKING TRIGGERS
-- ============================================

-- Trigger: Auto-insert expense when Flight booking is created
DELIMITER //
CREATE TRIGGER after_flight_booking_insert
AFTER INSERT ON flight_bookings
FOR EACH ROW
BEGIN
    -- Insert into expenses table when booking is confirmed
    IF NEW.booking_status = 'Confirmed' THEN
        INSERT INTO expenses (user_id, category, amount, description, expense_date, created_at)
        VALUES (
            NEW.user_id,
            'FLIGHT',
            NEW.total_fare,
            CONCAT('Flight Booking: ', NEW.from_airport, ' to ', NEW.to_airport, ' - ', NEW.passenger_name, ' (Ref: ', NEW.booking_reference, ')'),
            NEW.journey_date,
            NOW()
        );
    END IF;
END//
DELIMITER ;

-- Trigger: Update expense when Flight booking status changes
DELIMITER //
CREATE TRIGGER after_flight_booking_update
AFTER UPDATE ON flight_bookings
FOR EACH ROW
BEGIN
    -- If booking was just confirmed, add expense
    IF OLD.booking_status != 'Confirmed' AND NEW.booking_status = 'Confirmed' THEN
        INSERT INTO expenses (user_id, category, amount, description, expense_date, created_at)
        VALUES (
            NEW.user_id,
            'FLIGHT',
            NEW.total_fare,
            CONCAT('Flight Booking: ', NEW.from_airport, ' to ', NEW.to_airport, ' - ', NEW.passenger_name, ' (Ref: ', NEW.booking_reference, ')'),
            NEW.journey_date,
            NOW()
        );
    END IF;
    
    -- If booking was cancelled, remove expense
    IF OLD.booking_status = 'Confirmed' AND NEW.booking_status = 'Cancelled' THEN
        DELETE FROM expenses 
        WHERE user_id = NEW.user_id 
        AND category = 'FLIGHT' 
        AND description LIKE CONCAT('%Ref: ', NEW.booking_reference, '%')
        LIMIT 1;
    END IF;
END//
DELIMITER ;

-- ============================================
-- VERIFY TRIGGERS CREATED
-- ============================================

SELECT 
    TRIGGER_NAME,
    EVENT_MANIPULATION,
    EVENT_OBJECT_TABLE,
    ACTION_TIMING,
    ACTION_STATEMENT
FROM information_schema.TRIGGERS
WHERE TRIGGER_SCHEMA = 'transport_system'
ORDER BY EVENT_OBJECT_TABLE, ACTION_TIMING, EVENT_MANIPULATION;

SELECT '✅ All triggers created successfully!' AS Status;
