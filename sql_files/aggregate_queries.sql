-- ============================================================
-- AGGREGATE QUERIES
-- Multi-Modal Transport System Database
-- All queries using SUM, COUNT, AVG, MAX, MIN, GROUP BY
-- ============================================================

USE transport_system;

-- ============================================================
-- 1. REVENUE SUMMARY BY TRANSPORT MODE
-- ============================================================
-- Shows comprehensive statistics for each transport mode
-- Uses: COUNT, SUM, AVG, MAX, MIN

SELECT 
    'KSRTC' as transport_mode,
    COUNT(*) as total_bookings,
    COUNT(CASE WHEN booking_status = 'Confirmed' THEN 1 END) as confirmed_bookings,
    COUNT(CASE WHEN booking_status = 'Cancelled' THEN 1 END) as cancelled_bookings,
    SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END) as total_revenue,
    AVG(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END) as avg_fare,
    MAX(total_fare) as max_fare,
    MIN(total_fare) as min_fare
FROM ksrtc_bookings

UNION ALL

SELECT 
    'Train' as transport_mode,
    COUNT(*) as total_bookings,
    COUNT(CASE WHEN booking_status = 'Confirmed' THEN 1 END) as confirmed_bookings,
    COUNT(CASE WHEN booking_status = 'Cancelled' THEN 1 END) as cancelled_bookings,
    SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END) as total_revenue,
    AVG(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END) as avg_fare,
    MAX(total_fare) as max_fare,
    MIN(total_fare) as min_fare
FROM train_bookings

UNION ALL

SELECT 
    'Flight' as transport_mode,
    COUNT(*) as total_bookings,
    COUNT(CASE WHEN booking_status = 'Confirmed' THEN 1 END) as confirmed_bookings,
    COUNT(CASE WHEN booking_status = 'Cancelled' THEN 1 END) as cancelled_bookings,
    SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END) as total_revenue,
    AVG(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END) as avg_fare,
    MAX(total_fare) as max_fare,
    MIN(total_fare) as min_fare
FROM flight_bookings;

-- ============================================================
-- 2. MONTHLY BOOKING TRENDS
-- ============================================================
-- Aggregates bookings by month across all transport modes
-- Uses: DATE_FORMAT, COUNT, SUM, AVG, GROUP BY, ORDER BY

SELECT 
    DATE_FORMAT(journey_date, '%Y-%m') as month,
    DATE_FORMAT(journey_date, '%M %Y') as month_name,
    COUNT(*) as total_bookings,
    SUM(total_fare) as monthly_revenue,
    AVG(total_fare) as avg_booking_value,
    MAX(total_fare) as highest_booking,
    MIN(total_fare) as lowest_booking
FROM (
    SELECT journey_date, total_fare FROM ksrtc_bookings WHERE booking_status = 'Confirmed'
    UNION ALL
    SELECT journey_date, total_fare FROM train_bookings WHERE booking_status = 'Confirmed'
    UNION ALL
    SELECT journey_date, total_fare FROM flight_bookings WHERE booking_status = 'Confirmed'
) as all_bookings
GROUP BY month, month_name
ORDER BY month DESC
LIMIT 12;

-- ============================================================
-- 3. PEAK BOOKING HOURS ANALYSIS
-- ============================================================
-- Identifies busiest hours for bookings
-- Uses: HOUR, COUNT, SUM, AVG, GROUP BY, ORDER BY

SELECT 
    HOUR(booking_time) as booking_hour,
    CONCAT(LPAD(HOUR(booking_time), 2, '0'), ':00') as hour_label,
    COUNT(*) as total_bookings,
    SUM(total_fare) as hourly_revenue,
    AVG(total_fare) as avg_booking_value,
    MAX(total_fare) as max_booking
FROM (
    SELECT booking_time, total_fare FROM ksrtc_bookings
    UNION ALL
    SELECT booking_time, total_fare FROM train_bookings
    UNION ALL
    SELECT booking_time, total_fare FROM flight_bookings
) as all_bookings
GROUP BY booking_hour, hour_label
ORDER BY total_bookings DESC;

-- ============================================================
-- 4. USER SPENDING SUMMARY
-- ============================================================
-- Total spending per user across all modes
-- Uses: SUM, COUNT, GROUP BY, HAVING

SELECT 
    u.user_id,
    u.username,
    u.email,
    COUNT(DISTINCT booking_data.booking_id) as total_bookings,
    SUM(booking_data.total_fare) as total_spent,
    AVG(booking_data.total_fare) as avg_booking_value,
    MAX(booking_data.total_fare) as highest_booking,
    MIN(booking_data.total_fare) as lowest_booking
FROM users u
JOIN (
    SELECT user_id, booking_id, total_fare FROM ksrtc_bookings WHERE booking_status = 'Confirmed'
    UNION ALL
    SELECT user_id, booking_id, total_fare FROM train_bookings WHERE booking_status = 'Confirmed'
    UNION ALL
    SELECT user_id, booking_id, total_fare FROM flight_bookings WHERE booking_status = 'Confirmed'
) as booking_data ON u.user_id = booking_data.user_id
GROUP BY u.user_id, u.username, u.email
HAVING total_spent > 0
ORDER BY total_spent DESC
LIMIT 20;

-- ============================================================
-- 5. DAILY REVENUE BREAKDOWN
-- ============================================================
-- Revenue by date for each transport mode
-- Uses: DATE, COUNT, SUM, GROUP BY

SELECT 
    DATE(journey_date) as booking_date,
    SUM(CASE WHEN booking_type = 'KSRTC' THEN revenue ELSE 0 END) as ksrtc_revenue,
    SUM(CASE WHEN booking_type = 'Train' THEN revenue ELSE 0 END) as train_revenue,
    SUM(CASE WHEN booking_type = 'Flight' THEN revenue ELSE 0 END) as flight_revenue,
    SUM(revenue) as total_revenue,
    COUNT(*) as total_bookings
FROM (
    SELECT 'KSRTC' as booking_type, journey_date, total_fare as revenue 
    FROM ksrtc_bookings WHERE booking_status = 'Confirmed'
    UNION ALL
    SELECT 'Train' as booking_type, journey_date, total_fare as revenue 
    FROM train_bookings WHERE booking_status = 'Confirmed'
    UNION ALL
    SELECT 'Flight' as booking_type, journey_date, total_fare as revenue 
    FROM flight_bookings WHERE booking_status = 'Confirmed'
) as all_bookings
GROUP BY booking_date
ORDER BY booking_date DESC
LIMIT 30;

-- ============================================================
-- 6. POPULAR ROUTES BY BOOKINGS
-- ============================================================
-- Most booked routes for KSRTC
-- Uses: COUNT, GROUP BY, ORDER BY, LIMIT

SELECT 
    r.route_name,
    r.origin,
    r.destination,
    COUNT(kb.booking_id) as total_bookings,
    SUM(kb.total_fare) as total_revenue,
    AVG(kb.total_fare) as avg_fare
FROM ksrtc_bookings kb
JOIN ksrtc_schedules s ON kb.schedule_id = s.schedule_id
JOIN ksrtc_routes r ON s.route_id = r.route_id
WHERE kb.booking_status = 'Confirmed'
GROUP BY r.route_id, r.route_name, r.origin, r.destination
ORDER BY total_bookings DESC
LIMIT 10;

-- ============================================================
-- 7. TRAIN CLASS PREFERENCE ANALYSIS
-- ============================================================
-- Booking distribution by coach type
-- Uses: COUNT, SUM, AVG, GROUP BY

SELECT 
    coach_type,
    COUNT(*) as total_bookings,
    SUM(seat_count) as total_seats_booked,
    SUM(total_fare) as total_revenue,
    AVG(total_fare) as avg_fare,
    AVG(seat_count) as avg_seats_per_booking
FROM train_bookings
WHERE booking_status = 'Confirmed'
GROUP BY coach_type
ORDER BY total_bookings DESC;

-- ============================================================
-- 8. FLIGHT CLASS DISTRIBUTION
-- ============================================================
-- Revenue by flight class
-- Uses: COUNT, SUM, AVG, GROUP BY

SELECT 
    class_type,
    COUNT(*) as total_bookings,
    SUM(total_fare) as total_revenue,
    AVG(total_fare) as avg_fare,
    MAX(total_fare) as highest_fare,
    MIN(total_fare) as lowest_fare
FROM flight_bookings
WHERE booking_status = 'Confirmed'
GROUP BY class_type
ORDER BY total_revenue DESC;

-- ============================================================
-- 9. CANCELLATION STATISTICS
-- ============================================================
-- Cancellation rate by transport mode
-- Uses: COUNT, CASE WHEN, GROUP BY

SELECT 
    transport_mode,
    total_bookings,
    cancelled_bookings,
    ROUND((cancelled_bookings * 100.0 / total_bookings), 2) as cancellation_rate_percent,
    revenue_lost
FROM (
    SELECT 
        'KSRTC' as transport_mode,
        COUNT(*) as total_bookings,
        COUNT(CASE WHEN booking_status = 'Cancelled' THEN 1 END) as cancelled_bookings,
        SUM(CASE WHEN booking_status = 'Cancelled' THEN total_fare ELSE 0 END) as revenue_lost
    FROM ksrtc_bookings
    
    UNION ALL
    
    SELECT 
        'Train' as transport_mode,
        COUNT(*) as total_bookings,
        COUNT(CASE WHEN booking_status = 'Cancelled' THEN 1 END) as cancelled_bookings,
        SUM(CASE WHEN booking_status = 'Cancelled' THEN total_fare ELSE 0 END) as revenue_lost
    FROM train_bookings
    
    UNION ALL
    
    SELECT 
        'Flight' as transport_mode,
        COUNT(*) as total_bookings,
        COUNT(CASE WHEN booking_status = 'Cancelled' THEN 1 END) as cancelled_bookings,
        SUM(CASE WHEN booking_status = 'Cancelled' THEN total_fare ELSE 0 END) as revenue_lost
    FROM flight_bookings
) as cancellation_stats;

-- ============================================================
-- 10. WEEKDAY VS WEEKEND BOOKINGS
-- ============================================================
-- Booking pattern by day of week
-- Uses: DAYOFWEEK, DAYNAME, COUNT, SUM, GROUP BY

SELECT 
    DAYNAME(journey_date) as day_name,
    DAYOFWEEK(journey_date) as day_number,
    CASE 
        WHEN DAYOFWEEK(journey_date) IN (1, 7) THEN 'Weekend'
        ELSE 'Weekday'
    END as day_type,
    COUNT(*) as total_bookings,
    SUM(total_fare) as total_revenue,
    AVG(total_fare) as avg_booking_value
FROM (
    SELECT journey_date, total_fare FROM ksrtc_bookings WHERE booking_status = 'Confirmed'
    UNION ALL
    SELECT journey_date, total_fare FROM train_bookings WHERE booking_status = 'Confirmed'
    UNION ALL
    SELECT journey_date, total_fare FROM flight_bookings WHERE booking_status = 'Confirmed'
) as all_bookings
GROUP BY day_name, day_number, day_type
ORDER BY day_number;

-- ============================================================
-- 11. TOP SPENDING USERS BY MONTH
-- ============================================================
-- Monthly top spenders
-- Uses: DATE_FORMAT, SUM, GROUP BY, ORDER BY, LIMIT

SELECT 
    DATE_FORMAT(journey_date, '%Y-%m') as month,
    u.username,
    u.email,
    COUNT(*) as bookings_count,
    SUM(booking_data.total_fare) as total_spent
FROM users u
JOIN (
    SELECT user_id, journey_date, total_fare FROM ksrtc_bookings WHERE booking_status = 'Confirmed'
    UNION ALL
    SELECT user_id, journey_date, total_fare FROM train_bookings WHERE booking_status = 'Confirmed'
    UNION ALL
    SELECT user_id, journey_date, total_fare FROM flight_bookings WHERE booking_status = 'Confirmed'
) as booking_data ON u.user_id = booking_data.user_id
GROUP BY month, u.user_id, u.username, u.email
HAVING total_spent > 1000
ORDER BY month DESC, total_spent DESC
LIMIT 50;

-- ============================================================
-- 12. AVERAGE BOOKING VALUE BY TRANSPORT MODE AND MONTH
-- ============================================================
-- Trend analysis of booking values
-- Uses: DATE_FORMAT, AVG, COUNT, GROUP BY

SELECT 
    DATE_FORMAT(journey_date, '%Y-%m') as month,
    'KSRTC' as mode,
    AVG(total_fare) as avg_booking_value,
    COUNT(*) as booking_count
FROM ksrtc_bookings
WHERE booking_status = 'Confirmed'
GROUP BY month

UNION ALL

SELECT 
    DATE_FORMAT(journey_date, '%Y-%m') as month,
    'Train' as mode,
    AVG(total_fare) as avg_booking_value,
    COUNT(*) as booking_count
FROM train_bookings
WHERE booking_status = 'Confirmed'
GROUP BY month

UNION ALL

SELECT 
    DATE_FORMAT(journey_date, '%Y-%m') as month,
    'Flight' as mode,
    AVG(total_fare) as avg_booking_value,
    COUNT(*) as booking_count
FROM flight_bookings
WHERE booking_status = 'Confirmed'
GROUP BY month

ORDER BY month DESC, mode;

-- ============================================================
-- END OF AGGREGATE QUERIES
-- ============================================================
