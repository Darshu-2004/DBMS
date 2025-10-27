-- =============================================
-- TRANSPORT SYSTEM - TRIGGERS, PROCEDURES & FUNCTIONS 
-- =============================================
USE transport_system;

-- ============================================================
-- TRIGGERS
-- ============================================================

-- Trigger: Automatically mark trips as 'completed' once arrival_time is past current time
DELIMITER //
CREATE TRIGGER trg_update_trip_status
BEFORE UPDATE ON Trip
FOR EACH ROW
BEGIN
    IF NEW.arrival_time < NOW() AND NEW.status = 'scheduled' THEN
        SET NEW.status = 'completed';
    END IF;
END //
DELIMITER ;

-- Trigger: Automatically create a Payment record when a new Ticket is inserted
DELIMITER //
CREATE TRIGGER trg_auto_payment
AFTER INSERT ON Ticket
FOR EACH ROW
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Payment WHERE ticket_id = NEW.ticket_id) THEN
        INSERT INTO Payment (ticket_id, amount, payment_time, method, status)
        VALUES (NEW.ticket_id, 0.00, NOW(), 'wallet', 'failed');
    END IF;
END //
DELIMITER ;

-- Trigger: Prevent deletion of vehicles that are still assigned to operators
DELIMITER //
CREATE TRIGGER trg_prevent_vehicle_delete
BEFORE DELETE ON Vehicle
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT 1 FROM Vehicle_Assignment WHERE vehicle_id = OLD.vehicle_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Cannot delete Vehicle: it is currently assigned to an operator.';
    END IF;
END //
DELIMITER ;

-- Create table for logging announcement changes
CREATE TABLE IF NOT EXISTS Announcement_Log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    announcement_id INT,
    action ENUM('INSERT','UPDATE','DELETE'),
    action_time DATETIME,
    message TEXT
);

-- Trigger: Log every new announcement to Announcement_Log table
DELIMITER //
CREATE TRIGGER trg_log_announcement
AFTER INSERT ON Announcement
FOR EACH ROW
BEGIN
    INSERT INTO Announcement_Log (announcement_id, action, action_time, message)
    VALUES (NEW.announcement_id, 'INSERT', NOW(), NEW.message);
END //
DELIMITER ;

-- ============================================================
-- STORED PROCEDURES
-- ============================================================

-- Procedure: BookTicket
-- Description: Books a ticket for a user and creates a corresponding payment record.
DELIMITER //
CREATE PROCEDURE BookTicket (
    IN p_user_id INT,
    IN p_trip_id INT,
    IN p_seat_number VARCHAR(10),
    IN p_amount DECIMAL(10,2),
    IN p_payment_method ENUM('credit_card','debit_card','wallet','cash')
)
BEGIN
    DECLARE v_ticket_id INT;

    INSERT INTO Ticket (user_id, trip_id, purchase_time, seat_number, status)
    VALUES (p_user_id, p_trip_id, NOW(), p_seat_number, 'booked');

    SET v_ticket_id = LAST_INSERT_ID();

    INSERT INTO Payment (ticket_id, amount, payment_time, method, status)
    VALUES (v_ticket_id, p_amount, NOW(), p_payment_method, 'success');
END //
DELIMITER ;

-- Procedure: CancelTicket
-- Description: Cancels a ticket and automatically refunds the payment.
DELIMITER //
CREATE PROCEDURE CancelTicket (IN p_ticket_id INT)
BEGIN
    UPDATE Ticket
    SET status = 'cancelled'
    WHERE ticket_id = p_ticket_id;

    UPDATE Payment
    SET status = 'refunded'
    WHERE ticket_id = p_ticket_id;
END //
DELIMITER ;

-- Procedure: GetUserTrips
-- Description: Retrieves all trips booked by a specific user along with payment status.
DELIMITER //
CREATE PROCEDURE GetUserTrips (IN p_user_id INT)
BEGIN
    SELECT T.ticket_id, Tr.trip_id, Tr.status AS trip_status, P.amount, P.status AS payment_status
    FROM Ticket T
    JOIN Trip Tr ON T.trip_id = Tr.trip_id
    JOIN Payment P ON T.ticket_id = P.ticket_id
    WHERE T.user_id = p_user_id;
END //
DELIMITER ;

-- Procedure: AssignVehicle
-- Description: Assigns a vehicle to an operator for a specific time duration.
DELIMITER //
CREATE PROCEDURE AssignVehicle (
    IN p_vehicle_id INT,
    IN p_operator_id INT,
    IN p_start DATETIME,
    IN p_end DATETIME
)
BEGIN
    INSERT INTO Vehicle_Assignment (vehicle_id, operator_id, assignment_start, assignment_end)
    VALUES (p_vehicle_id, p_operator_id, p_start, p_end);
END //
DELIMITER ;

-- ============================================================
-- FUNCTIONS
-- ============================================================

-- Function: GetTripDuration
-- Description: Returns the duration (in minutes) between a trip's departure and arrival.
DELIMITER //
CREATE FUNCTION GetTripDuration(p_trip_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE v_depart DATETIME;
    DECLARE v_arrive DATETIME;
    DECLARE v_duration INT;

    SELECT departure_time, arrival_time INTO v_depart, v_arrive
    FROM Trip WHERE trip_id = p_trip_id;

    SET v_duration = TIMESTAMPDIFF(MINUTE, v_depart, v_arrive);
    RETURN v_duration;
END //
DELIMITER ;

-- Function: GetUserTotalSpend
-- Description: Calculates the total successful payments made by a user.
DELIMITER //
CREATE FUNCTION GetUserTotalSpend(p_user_id INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total DECIMAL(10,2);

    SELECT SUM(P.amount)
    INTO total
    FROM Payment P
    JOIN Ticket T ON P.ticket_id = T.ticket_id
    WHERE T.user_id = p_user_id
    AND P.status = 'success';

    RETURN IFNULL(total, 0.00);
END //
DELIMITER ;

-- Function: IsVehicleAvailable
-- Description: Returns TRUE if the given vehicle is active (available), else FALSE.
DELIMITER //
CREATE FUNCTION IsVehicleAvailable(p_vehicle_id INT)
RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    DECLARE v_status ENUM('active','maintenance','decommissioned');
    SELECT status INTO v_status FROM Vehicle WHERE vehicle_id = p_vehicle_id;
    RETURN v_status = 'active';
END //
DELIMITER ;
