-- =============================================
-- TRANSPORT SYSTEM 
-- =============================================
USE transport;

-- ============================================================
-- 1️⃣ TRIGGERS TESTS
-- ============================================================

-- Test 1: Update a Trip so that arrival_time is in the past.
-- Expected: Trigger 'trg_update_trip_status' should automatically mark it as 'completed'.
UPDATE Trip
SET arrival_time = NOW() - INTERVAL 1 HOUR
WHERE trip_id = 1;
SELECT trip_id, status FROM Trip WHERE trip_id = 1;

-- Test 2: Insert a new Ticket and check if Payment is auto-created.
-- Expected: Trigger 'trg_auto_payment' should add a Payment with amount=0 and status='failed'.
INSERT INTO Ticket (user_id, trip_id, purchase_time, seat_number, status)
VALUES (1, 1, NOW(), '22C', 'booked');
SELECT * FROM Payment WHERE ticket_id = LAST_INSERT_ID();

-- Test 3: Attempt to delete a Vehicle that has an assignment.
-- Expected: Trigger 'trg_prevent_vehicle_delete' should block the deletion with an error.
DELETE FROM Vehicle WHERE vehicle_id = 1;

-- Test 4: Insert a new Announcement.
-- Expected: Trigger 'trg_log_announcement' should log the entry into Announcement_Log.
INSERT INTO Announcement (station_id, message, announcement_time, type)
VALUES (1, 'System maintenance alert', NOW(), 'info');
SELECT * FROM Announcement_Log ORDER BY log_id DESC LIMIT 1;

-- ============================================================
-- 2️⃣ PROCEDURES TESTS
-- ============================================================

-- Test 5: Call BookTicket procedure to book a ticket and create a payment record.
-- Expected: New Ticket and corresponding Payment should appear with status 'success'.
CALL BookTicket(1, 2, '15B', 500.00, 'credit_card');
SELECT * FROM Ticket ORDER BY ticket_id DESC LIMIT 1;
SELECT * FROM Payment ORDER BY payment_id DESC LIMIT 1;

-- Test 6: Call CancelTicket procedure to cancel a ticket and refund its payment.
-- Expected: Ticket status -> 'cancelled'; Payment status -> 'refunded'.
CALL CancelTicket(1);
SELECT ticket_id, status FROM Ticket WHERE ticket_id = 1;
SELECT payment_id, status FROM Payment WHERE ticket_id = 1;

-- Test 7: Retrieve all trips for a user.
-- Expected: Displays ticket, trip status, amount, and payment info for that user.
CALL GetUserTrips(1);

-- Test 8: Assign a vehicle to an operator.
-- Expected: Inserts a new record into Vehicle_Assignment table.
CALL AssignVehicle(1, 2, NOW(), NOW() + INTERVAL 8 HOUR);
SELECT * FROM Vehicle_Assignment ORDER BY assignment_id DESC LIMIT 1;

-- ============================================================
-- 3️⃣ FUNCTIONS TESTS
-- ============================================================

-- Test 9: Get trip durations in minutes using GetTripDuration function.
SELECT trip_id, GetTripDuration(trip_id) AS Duration_Minutes FROM Trip;

-- Test 10: Get total spend per user using GetUserTotalSpend function.
SELECT name, GetUserTotalSpend(user_id) AS Total_Spend FROM User;

-- Test 11: Check whether vehicles are active using IsVehicleAvailable function.
SELECT vehicle_id, IsVehicleAvailable(vehicle_id) AS Is_Available FROM Vehicle;

-- ============================================================
