-- USER
INSERT INTO User (name, email, password_hash, user_type) VALUES
('Amit Sharma', 'amit@gmail.com', 'hash123', 'passenger'),
('Riya Verma', 'riya@metro.in', 'hash456', 'operator'),
('Arjun Rao', 'arjun@admin.in', 'hash789', 'admin');

-- USER_PHONE
INSERT INTO User_Phone VALUES
(1, '9876543210'),
(1, '9123456789'),
(2, '9000123456');

-- STATION
INSERT INTO Station (name, location, type) VALUES
('Majestic', 'Bangalore', 'bus'),
('KSR Bengaluru', 'Bangalore', 'train'),
('Kempegowda Airport', 'Bangalore', 'airport');

-- ROUTE
INSERT INTO Route (mode, origin_station_id, destination_station_id, distance_km) VALUES
('bus', 1, 2, 10.5),
('train', 2, 3, 40.2),
('flight', 3, 1, 340.0);

-- VEHICLE
INSERT INTO Vehicle (route_id, type, capacity, registration_number, status) VALUES
(1, 'bus', 40, 'KA01AB1234', 'active'),
(2, 'train', 250, 'TR5678', 'active'),
(3, 'plane', 180, 'AI-203', 'maintenance');

-- OPERATOR
INSERT INTO Operator (name, contact_info, type) VALUES
('BMTC', '0801234567', 'government'),
('Indian Railways', '0112345678', 'government'),
('IndiGo', '0229876543', 'private');

-- VEHICLE_ASSIGNMENT
INSERT INTO Vehicle_Assignment (vehicle_id, operator_id, assignment_start, assignment_end) VALUES
(1, 1, '2025-10-09 06:00:00', '2025-10-09 22:00:00'),
(2, 2, '2025-10-09 09:00:00', '2025-10-09 20:00:00'),
(3, 3, '2025-10-10 05:00:00', '2025-10-10 17:00:00');

-- SCHEDULE
INSERT INTO Schedule (route_id, departure_time, arrival_time, frequency) VALUES
(1, '2025-10-09 07:00:00', '2025-10-09 07:45:00', 'daily'),
(2, '2025-10-09 09:00:00', '2025-10-09 12:00:00', 'daily'),
(3, '2025-10-10 06:00:00', '2025-10-10 09:00:00', 'weekly');

-- TRIP
INSERT INTO Trip (vehicle_id, route_id, schedule_id, departure_time, arrival_time, status) VALUES
(1, 1, 1, '2025-10-09 07:00:00', '2025-10-09 07:45:00', 'scheduled'),
(2, 2, 2, '2025-10-09 09:00:00', '2025-10-09 12:00:00', 'completed'),
(3, 3, 3, '2025-10-10 06:00:00', '2025-10-10 09:00:00', 'cancelled');

-- TICKET
INSERT INTO Ticket (user_id, trip_id, purchase_time, seat_number, status) VALUES
(1, 1, NOW(), '12A', 'booked'),
(1, 2, NOW(), 'B4', 'checked_in'),
(2, 3, NOW(), 'C5', 'cancelled');

-- PAYMENT
INSERT INTO Payment (ticket_id, amount, payment_time, method, status) VALUES
(1, 120.00, NOW(), 'wallet', 'success'),
(2, 600.00, NOW(), 'credit_card', 'success'),
(3, 1500.00, NOW(), 'debit_card', 'refunded');

-- INTERCHANGE
INSERT INTO Interchange VALUES
(1, 2, 'bus', 'train'),
(2, 3, 'train', 'flight'),
(3, 1, 'flight', 'bus');

-- ANNOUNCEMENT
INSERT INTO Announcement (station_id, message, announcement_time, type) VALUES
(1, 'Bus delayed due to traffic', NOW(), 'alert'),
(2, 'Train arriving on platform 2', NOW(), 'info'),
(3, 'Flight delayed due to weather', NOW(), 'emergency');





-- Update user email
UPDATE User SET email = 'amit_updated@gmail.com' WHERE user_id = 1;

-- Change vehicle status
UPDATE Vehicle SET status = 'active' WHERE vehicle_id = 3;

-- Modify schedule frequency
UPDATE Schedule SET frequency = 'monthly' WHERE schedule_id = 3;

-- Update ticket status
UPDATE Ticket SET status = 'checked_in' WHERE ticket_id = 1;

-- Change payment status
UPDATE Payment SET status = 'refunded' WHERE ticket_id = 2;





-- Delete cancelled tickets
DELETE FROM Ticket WHERE status = 'cancelled';

-- Remove an inactive vehicle
DELETE FROM Vehicle WHERE status = 'decommissioned';

-- Remove an old announcement
DELETE FROM Announcement WHERE announcement_id = 2;





-- select commands 

-- View all users and their phones
SELECT U.name, UP.phone_number 
FROM User U
JOIN User_Phone UP ON U.user_id = UP.user_id;

-- List all active vehicles with route info
SELECT V.vehicle_id, V.type, R.mode, R.distance_km
FROM Vehicle V
JOIN Route R ON V.route_id = R.route_id
WHERE V.status = 'active';

-- Show user tickets with trip and payment info
SELECT U.name, T.ticket_id, Tr.status AS trip_status, P.amount, P.status AS payment_status
FROM Ticket T
JOIN User U ON T.user_id = U.user_id
JOIN Trip Tr ON T.trip_id = Tr.trip_id
JOIN Payment P ON P.ticket_id = T.ticket_id;

-- List operators with assigned vehicles
SELECT O.name AS Operator, V.registration_number, VA.assignment_start, VA.assignment_end
FROM Vehicle_Assignment VA
JOIN Vehicle V ON VA.vehicle_id = V.vehicle_id
JOIN Operator O ON VA.operator_id = O.operator_id;

-- Get all announcements with station details
SELECT S.name AS Station, A.message, A.type
FROM Announcement A
JOIN Station S ON A.station_id = S.station_id;


