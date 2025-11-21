-- ============================================================
-- JOIN QUERIES
-- Multi-Modal Transport System Database
-- Complex queries using INNER JOIN, LEFT JOIN
-- ============================================================

USE transport_system;

-- ============================================================
-- 1. COMPLETE KSRTC BOOKING DETAILS WITH USER INFO
-- ============================================================
-- Joins: users, ksrtc_bookings, schedules, routes, buses

SELECT 
    u.username,
    u.email,
    u.phone_number,
    kb.booking_reference,
    kb.journey_date,
    r.route_name,
    r.origin as source,
    r.destination,
    r.distance_km,
    b.bus_number,
    b.bus_type,
    s.departure_time,
    s.arrival_time,
    kb.passenger_name,
    kb.passenger_age,
    kb.passenger_gender,
    kb.seat_numbers,
    kb.total_fare,
    kb.booking_status,
    kb.booking_time
FROM users u
INNER JOIN ksrtc_bookings kb ON u.user_id = kb.user_id
INNER JOIN ksrtc_schedules s ON kb.schedule_id = s.schedule_id
INNER JOIN ksrtc_routes r ON s.route_id = r.route_id
INNER JOIN ksrtc_buses b ON s.bus_id = b.bus_id
WHERE kb.booking_status = 'Confirmed'
ORDER BY kb.booking_time DESC
LIMIT 50;

-- ============================================================
-- 2. TRAIN BOOKINGS WITH COMPLETE JOURNEY INFO
-- ============================================================
-- Joins: users, train_bookings, trains, train_stations

SELECT 
    u.username,
    u.email,
    tb.pnr_number,
    t.train_number,
    t.train_name,
    t.train_type,
    tb.source_station,
    s1.station_name as source_station_name,
    s1.city as source_city,
    tb.destination_station,
    s2.station_name as destination_station_name,
    s2.city as destination_city,
    tb.journey_date,
    tb.coach_type,
    tb.seat_count,
    tb.berth_preference,
    tb.passenger_names,
    tb.berth_numbers,
    tb.total_fare,
    tb.booking_status,
    tb.booking_time
FROM users u
INNER JOIN train_bookings tb ON u.user_id = tb.user_id
INNER JOIN trains t ON tb.train_id = t.train_id
INNER JOIN train_stations s1 ON tb.source_station = s1.station_code
INNER JOIN train_stations s2 ON tb.destination_station = s2.station_code
WHERE tb.journey_date >= CURDATE()
ORDER BY tb.journey_date, tb.booking_time;

-- ============================================================
-- 3. FLIGHT BOOKINGS WITH AIRLINE AND AIRPORT DETAILS
-- ============================================================
-- Joins: users, flight_bookings, flights, airlines, airports

SELECT 
    u.username,
    u.email,
    fb.booking_reference,
    a.airline_name,
    a.airline_code,
    f.flight_number,
    ap1.airport_name as origin_airport,
    ap1.city as origin_city,
    ap1.airport_code as origin_code,
    ap2.airport_name as destination_airport,
    ap2.city as destination_city,
    ap2.airport_code as destination_code,
    fb.journey_date,
    fs.departure_time,
    fs.arrival_time,
    fs.duration_minutes,
    fb.class_type,
    fb.passenger_names,
    fb.seat_numbers,
    fb.total_fare,
    fb.booking_status,
    fb.booking_time
FROM users u
INNER JOIN flight_bookings fb ON u.user_id = fb.user_id
INNER JOIN flights f ON fb.flight_id = f.flight_id
INNER JOIN airlines a ON f.airline_id = a.airline_id
INNER JOIN airports ap1 ON f.origin_code = ap1.airport_code
INNER JOIN airports ap2 ON f.destination_code = ap2.airport_code
INNER JOIN flight_schedules fs ON f.flight_id = fs.flight_id
WHERE fb.booking_status = 'Confirmed'
ORDER BY fb.journey_date;

-- ============================================================
-- 4. USER BOOKING HISTORY ACROSS ALL MODES
-- ============================================================
-- Shows all bookings for a user with transport mode

SELECT 
    u.username,
    u.email,
    'KSRTC' as transport_mode,
    kb.booking_reference as reference,
    r.origin as source,
    r.destination,
    kb.journey_date,
    kb.total_fare,
    kb.booking_status,
    kb.booking_time
FROM users u
INNER JOIN ksrtc_bookings kb ON u.user_id = kb.user_id
INNER JOIN ksrtc_schedules s ON kb.schedule_id = s.schedule_id
INNER JOIN ksrtc_routes r ON s.route_id = r.route_id

UNION ALL

SELECT 
    u.username,
    u.email,
    'Train' as transport_mode,
    tb.pnr_number as reference,
    tb.source_station as source,
    tb.destination_station as destination,
    tb.journey_date,
    tb.total_fare,
    tb.booking_status,
    tb.booking_time
FROM users u
INNER JOIN train_bookings tb ON u.user_id = tb.user_id

UNION ALL

SELECT 
    u.username,
    u.email,
    'Flight' as transport_mode,
    fb.booking_reference as reference,
    ap1.city as source,
    ap2.city as destination,
    fb.journey_date,
    fb.total_fare,
    fb.booking_status,
    fb.booking_time
FROM users u
INNER JOIN flight_bookings fb ON u.user_id = fb.user_id
INNER JOIN flights f ON fb.flight_id = f.flight_id
INNER JOIN airports ap1 ON f.origin_code = ap1.airport_code
INNER JOIN airports ap2 ON f.destination_code = ap2.airport_code

ORDER BY booking_time DESC
LIMIT 100;

-- ============================================================
-- 5. POPULAR ROUTES WITH BOOKING COUNTS (KSRTC)
-- ============================================================
-- Joins routes with bookings to find popularity

SELECT 
    r.route_name,
    r.origin,
    r.destination,
    r.distance_km,
    r.base_fare,
    COUNT(kb.booking_id) as total_bookings,
    COUNT(CASE WHEN kb.booking_status = 'Confirmed' THEN 1 END) as confirmed_bookings,
    SUM(CASE WHEN kb.booking_status = 'Confirmed' THEN kb.total_fare ELSE 0 END) as total_revenue,
    AVG(CASE WHEN kb.booking_status = 'Confirmed' THEN kb.total_fare END) as avg_fare
FROM ksrtc_routes r
LEFT JOIN ksrtc_schedules s ON r.route_id = s.route_id
LEFT JOIN ksrtc_bookings kb ON s.schedule_id = kb.schedule_id
GROUP BY r.route_id, r.route_name, r.origin, r.destination, r.distance_km, r.base_fare
HAVING total_bookings > 0
ORDER BY total_bookings DESC
LIMIT 20;

-- ============================================================
-- 6. TRAIN ROUTE ANALYSIS WITH STATIONS
-- ============================================================
-- Shows train routes with source and destination details

SELECT 
    t.train_number,
    t.train_name,
    t.train_type,
    tb.source_station,
    s1.station_name as source_name,
    s1.city as source_city,
    tb.destination_station,
    s2.station_name as destination_name,
    s2.city as destination_city,
    COUNT(tb.booking_id) as total_bookings,
    SUM(tb.total_fare) as total_revenue,
    AVG(tb.total_fare) as avg_fare
FROM trains t
INNER JOIN train_bookings tb ON t.train_id = tb.train_id
INNER JOIN train_stations s1 ON tb.source_station = s1.station_code
INNER JOIN train_stations s2 ON tb.destination_station = s2.station_code
WHERE tb.booking_status = 'Confirmed'
GROUP BY t.train_id, t.train_number, t.train_name, t.train_type,
         tb.source_station, s1.station_name, s1.city,
         tb.destination_station, s2.station_name, s2.city
ORDER BY total_bookings DESC
LIMIT 30;

-- ============================================================
-- 7. FLIGHT ROUTE POPULARITY WITH AIRLINE INFO
-- ============================================================
-- Shows popular flight routes with airline details

SELECT 
    a.airline_name,
    f.flight_number,
    ap1.city as origin_city,
    ap1.airport_name as origin_airport,
    ap2.city as destination_city,
    ap2.airport_name as destination_airport,
    COUNT(fb.booking_id) as total_bookings,
    SUM(fb.total_fare) as total_revenue,
    AVG(fb.total_fare) as avg_fare,
    COUNT(CASE WHEN fb.class_type = 'Economy' THEN 1 END) as economy_bookings,
    COUNT(CASE WHEN fb.class_type = 'Business' THEN 1 END) as business_bookings,
    COUNT(CASE WHEN fb.class_type = 'First' THEN 1 END) as first_class_bookings
FROM airlines a
INNER JOIN flights f ON a.airline_id = f.airline_id
INNER JOIN airports ap1 ON f.origin_code = ap1.airport_code
INNER JOIN airports ap2 ON f.destination_code = ap2.airport_code
INNER JOIN flight_bookings fb ON f.flight_id = fb.flight_id
WHERE fb.booking_status = 'Confirmed'
GROUP BY a.airline_id, a.airline_name, f.flight_id, f.flight_number,
         ap1.city, ap1.airport_name, ap2.city, ap2.airport_name
ORDER BY total_bookings DESC
LIMIT 25;

-- ============================================================
-- 8. USERS WITH MULTI-MODAL BOOKINGS
-- ============================================================
-- Find users who have used multiple transport modes

SELECT 
    u.user_id,
    u.username,
    u.email,
    COUNT(CASE WHEN booking_data.mode = 'KSRTC' THEN 1 END) as ksrtc_bookings,
    COUNT(CASE WHEN booking_data.mode = 'Train' THEN 1 END) as train_bookings,
    COUNT(CASE WHEN booking_data.mode = 'Flight' THEN 1 END) as flight_bookings,
    COUNT(DISTINCT booking_data.mode) as modes_used,
    COUNT(*) as total_bookings,
    SUM(booking_data.fare) as total_spent
FROM users u
INNER JOIN (
    SELECT user_id, 'KSRTC' as mode, total_fare as fare FROM ksrtc_bookings WHERE booking_status = 'Confirmed'
    UNION ALL
    SELECT user_id, 'Train' as mode, total_fare as fare FROM train_bookings WHERE booking_status = 'Confirmed'
    UNION ALL
    SELECT user_id, 'Flight' as mode, total_fare as fare FROM flight_bookings WHERE booking_status = 'Confirmed'
) as booking_data ON u.user_id = booking_data.user_id
GROUP BY u.user_id, u.username, u.email
HAVING modes_used > 1
ORDER BY modes_used DESC, total_bookings DESC;

-- ============================================================
-- 9. BOOKING ACTIVITY LOG WITH USER DETAILS
-- ============================================================
-- Shows trigger log with user information

SELECT 
    bal.log_id,
    bal.booking_type,
    bal.booking_reference,
    u.username,
    u.email,
    bal.action_type,
    bal.old_status,
    bal.new_status,
    bal.total_fare,
    bal.journey_date,
    bal.log_timestamp
FROM booking_activity_log bal
INNER JOIN users u ON bal.user_id = u.user_id
ORDER BY bal.log_timestamp DESC
LIMIT 100;

-- ============================================================
-- 10. SEAT AVAILABILITY BY BUS TYPE
-- ============================================================
-- Shows bus types with seat statistics

SELECT 
    b.bus_type,
    COUNT(DISTINCT b.bus_id) as total_buses,
    SUM(b.total_seats) as total_seats,
    COUNT(s.seat_id) as seats_configured,
    COUNT(CASE WHEN s.is_available = TRUE THEN 1 END) as available_seats,
    COUNT(CASE WHEN s.is_available = FALSE THEN 1 END) as booked_seats,
    ROUND((COUNT(CASE WHEN s.is_available = FALSE THEN 1 END) * 100.0 / COUNT(s.seat_id)), 2) as occupancy_percent
FROM ksrtc_buses b
LEFT JOIN ksrtc_seats s ON b.bus_id = s.bus_id
WHERE b.is_active = TRUE
GROUP BY b.bus_type
ORDER BY total_buses DESC;

-- ============================================================
-- 11. TRAIN COACH AVAILABILITY
-- ============================================================
-- Shows coach types with booking statistics

SELECT 
    t.train_number,
    t.train_name,
    tc.coach_type,
    tc.coach_count,
    tc.seats_per_coach,
    (tc.coach_count * tc.seats_per_coach) as total_capacity,
    COUNT(tb.booking_id) as bookings_count,
    SUM(tb.seat_count) as seats_booked,
    tc.base_fare,
    SUM(tb.total_fare) as revenue_generated
FROM trains t
INNER JOIN train_coaches tc ON t.train_id = tc.train_id
LEFT JOIN train_bookings tb ON t.train_id = tb.train_id AND tc.coach_type = tb.coach_type
WHERE tb.booking_status = 'Confirmed' OR tb.booking_id IS NULL
GROUP BY t.train_id, t.train_number, t.train_name, tc.coach_type, 
         tc.coach_count, tc.seats_per_coach, tc.base_fare
ORDER BY t.train_number, tc.coach_type;

-- ============================================================
-- 12. COMPREHENSIVE USER ANALYTICS
-- ============================================================
-- Complete user profile with all booking details

SELECT 
    u.user_id,
    u.username,
    u.email,
    u.full_name,
    u.phone_number,
    u.created_at as registration_date,
    u.last_login,
    DATEDIFF(CURDATE(), u.created_at) as days_as_member,
    stats.total_bookings,
    stats.total_spent,
    stats.avg_booking_value,
    stats.ksrtc_count,
    stats.train_count,
    stats.flight_count
FROM users u
LEFT JOIN (
    SELECT 
        user_id,
        COUNT(*) as total_bookings,
        SUM(fare) as total_spent,
        AVG(fare) as avg_booking_value,
        COUNT(CASE WHEN mode = 'KSRTC' THEN 1 END) as ksrtc_count,
        COUNT(CASE WHEN mode = 'Train' THEN 1 END) as train_count,
        COUNT(CASE WHEN mode = 'Flight' THEN 1 END) as flight_count
    FROM (
        SELECT user_id, 'KSRTC' as mode, total_fare as fare FROM ksrtc_bookings WHERE booking_status = 'Confirmed'
        UNION ALL
        SELECT user_id, 'Train' as mode, total_fare as fare FROM train_bookings WHERE booking_status = 'Confirmed'
        UNION ALL
        SELECT user_id, 'Flight' as mode, total_fare as fare FROM flight_bookings WHERE booking_status = 'Confirmed'
    ) as all_bookings
    GROUP BY user_id
) as stats ON u.user_id = stats.user_id
WHERE u.user_type = 'user'
ORDER BY stats.total_spent DESC;

-- ============================================================
-- END OF JOIN QUERIES
-- ============================================================
