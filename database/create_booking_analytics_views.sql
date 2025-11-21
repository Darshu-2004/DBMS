-- Create Admin Analytics Views for KSRTC, Train, and Flight Bookings
USE transport_system;

-- KSRTC Booking Statistics
DROP VIEW IF EXISTS v_ksrtc_booking_stats;
CREATE VIEW v_ksrtc_booking_stats AS
SELECT 
    'KSRTC Bus' as transport_type,
    COUNT(*) as total_bookings,
    SUM(CASE WHEN booking_status = 'Confirmed' THEN 1 ELSE 0 END) as confirmed_bookings,
    SUM(CASE WHEN booking_status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled_bookings,
    ROUND(AVG(total_fare), 2) as avg_fare,
    ROUND(SUM(total_fare), 2) as total_revenue,
    COUNT(DISTINCT user_id) as unique_users
FROM ksrtc_bookings;

-- Train Booking Statistics
DROP VIEW IF EXISTS v_train_booking_stats;
CREATE VIEW v_train_booking_stats AS
SELECT 
    'Train' as transport_type,
    COUNT(*) as total_bookings,
    SUM(CASE WHEN booking_status = 'Confirmed' THEN 1 ELSE 0 END) as confirmed_bookings,
    SUM(CASE WHEN booking_status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled_bookings,
    ROUND(AVG(total_fare), 2) as avg_fare,
    ROUND(SUM(total_fare), 2) as total_revenue,
    COUNT(DISTINCT user_id) as unique_users
FROM train_bookings;

-- Flight Booking Statistics
DROP VIEW IF EXISTS v_flight_booking_stats;
CREATE VIEW v_flight_booking_stats AS
SELECT 
    'Flight' as transport_type,
    COUNT(*) as total_bookings,
    SUM(CASE WHEN booking_status = 'Confirmed' THEN 1 ELSE 0 END) as confirmed_bookings,
    SUM(CASE WHEN booking_status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled_bookings,
    ROUND(AVG(total_fare), 2) as avg_fare,
    ROUND(SUM(total_fare), 2) as total_revenue,
    COUNT(DISTINCT user_id) as unique_users
FROM flight_bookings;

-- Combined Booking Statistics
DROP VIEW IF EXISTS v_all_booking_stats;
CREATE VIEW v_all_booking_stats AS
SELECT * FROM v_ksrtc_booking_stats
UNION ALL
SELECT * FROM v_train_booking_stats
UNION ALL
SELECT * FROM v_flight_booking_stats;

-- Popular Train Routes
DROP VIEW IF EXISTS v_popular_train_routes;
CREATE VIEW v_popular_train_routes AS
SELECT 
    from_station,
    to_station,
    COUNT(*) as booking_count,
    ROUND(SUM(total_fare), 2) as total_revenue
FROM train_bookings
WHERE booking_status = 'Confirmed'
GROUP BY from_station, to_station
ORDER BY booking_count DESC
LIMIT 10;

-- Popular Flight Routes
DROP VIEW IF EXISTS v_popular_flight_routes;
CREATE VIEW v_popular_flight_routes AS
SELECT 
    from_airport,
    to_airport,
    COUNT(*) as booking_count,
    ROUND(SUM(total_fare), 2) as total_revenue
FROM flight_bookings
WHERE booking_status = 'Confirmed'
GROUP BY from_airport, to_airport
ORDER BY booking_count DESC
LIMIT 10;

-- Popular KSRTC Routes
DROP VIEW IF EXISTS v_popular_ksrtc_routes;
CREATE VIEW v_popular_ksrtc_routes AS
SELECT 
    boarding_stop,
    destination_stop,
    COUNT(*) as booking_count,
    ROUND(SUM(total_fare), 2) as total_revenue
FROM ksrtc_bookings
WHERE booking_status = 'Confirmed'
GROUP BY boarding_stop, destination_stop
ORDER BY booking_count DESC
LIMIT 10;

-- User Expense Summary (All Transport Types)
DROP VIEW IF EXISTS v_user_expense_summary;
CREATE VIEW v_user_expense_summary AS
SELECT 
    u.user_id,
    u.username,
    u.full_name,
    COALESCE(ke.total_ksrtc, 0) + COALESCE(te.total_train, 0) + COALESCE(fe.total_flight, 0) as total_expenses,
    COALESCE(kb.ksrtc_count, 0) as ksrtc_bookings,
    COALESCE(tb.train_count, 0) as train_bookings,
    COALESCE(fb.flight_count, 0) as flight_bookings
FROM users u
LEFT JOIN (
    SELECT user_id, SUM(amount) as total_ksrtc FROM ksrtc_user_expenses GROUP BY user_id
) ke ON u.user_id = ke.user_id
LEFT JOIN (
    SELECT user_id, SUM(amount) as total_train FROM train_user_expenses GROUP BY user_id
) te ON u.user_id = te.user_id
LEFT JOIN (
    SELECT user_id, SUM(amount) as total_flight FROM flight_user_expenses GROUP BY user_id
) fe ON u.user_id = fe.user_id
LEFT JOIN (
    SELECT user_id, COUNT(*) as ksrtc_count FROM ksrtc_bookings GROUP BY user_id
) kb ON u.user_id = kb.user_id
LEFT JOIN (
    SELECT user_id, COUNT(*) as train_count FROM train_bookings GROUP BY user_id
) tb ON u.user_id = tb.user_id
LEFT JOIN (
    SELECT user_id, COUNT(*) as flight_count FROM flight_bookings GROUP BY user_id
) fb ON u.user_id = fb.user_id
WHERE u.user_type = 'user'
ORDER BY total_expenses DESC;

-- Daily Booking Trends (Last 30 days)
DROP VIEW IF EXISTS v_daily_booking_trends;
CREATE VIEW v_daily_booking_trends AS
SELECT 
    journey_date as date,
    'KSRTC' as transport_type,
    COUNT(*) as bookings,
    SUM(total_fare) as revenue
FROM ksrtc_bookings
WHERE journey_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY journey_date
UNION ALL
SELECT 
    DATE(booked_at) as date,
    'Train' as transport_type,
    COUNT(*) as bookings,
    SUM(total_fare) as revenue
FROM train_bookings
WHERE DATE(booked_at) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY DATE(booked_at)
UNION ALL
SELECT 
    DATE(booked_at) as date,
    'Flight' as transport_type,
    COUNT(*) as bookings,
    SUM(total_fare) as revenue
FROM flight_bookings
WHERE DATE(booked_at) >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
GROUP BY DATE(booked_at)
ORDER BY date DESC;

-- Peak Booking Hours
DROP VIEW IF EXISTS v_peak_booking_hours;
CREATE VIEW v_peak_booking_hours AS
SELECT 
    HOUR(booked_at) as hour,
    COUNT(*) as booking_count
FROM (
    SELECT booked_at FROM train_bookings
    UNION ALL
    SELECT booked_at FROM flight_bookings
) as all_bookings
GROUP BY HOUR(booked_at)
ORDER BY booking_count DESC;

SELECT 'Booking analytics views created successfully!' AS Status;
