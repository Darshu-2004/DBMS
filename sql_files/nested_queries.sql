-- ============================================================
-- NESTED QUERIES (SUBQUERIES)
-- Multi-Modal Transport System Database
-- Complex queries using subqueries in WHERE, FROM, SELECT
-- ============================================================

USE transport_system;

-- ============================================================
-- 1. USERS WHO SPENT MORE THAN AVERAGE
-- ============================================================
-- Subquery: Calculate average spending, then filter users above it

SELECT 
    u.user_id,
    u.username,
    u.email,
    (
        SELECT COALESCE(SUM(total_fare), 0) 
        FROM ksrtc_bookings kb 
        WHERE kb.user_id = u.user_id AND kb.booking_status = 'Confirmed'
    ) +
    (
        SELECT COALESCE(SUM(total_fare), 0) 
        FROM train_bookings tb 
        WHERE tb.user_id = u.user_id AND tb.booking_status = 'Confirmed'
    ) +
    (
        SELECT COALESCE(SUM(total_fare), 0) 
        FROM flight_bookings fb 
        WHERE fb.user_id = u.user_id AND fb.booking_status = 'Confirmed'
    ) as total_expense
FROM users u
WHERE (
    (
        SELECT COALESCE(SUM(total_fare), 0) 
        FROM ksrtc_bookings kb 
        WHERE kb.user_id = u.user_id AND kb.booking_status = 'Confirmed'
    ) +
    (
        SELECT COALESCE(SUM(total_fare), 0) 
        FROM train_bookings tb 
        WHERE tb.user_id = u.user_id AND tb.booking_status = 'Confirmed'
    ) +
    (
        SELECT COALESCE(SUM(total_fare), 0) 
        FROM flight_bookings fb 
        WHERE fb.user_id = u.user_id AND fb.booking_status = 'Confirmed'
    )
) > (
    -- Calculate overall average spending
    SELECT AVG(total) FROM (
        SELECT SUM(total_fare) as total 
        FROM ksrtc_bookings 
        WHERE booking_status = 'Confirmed'
        GROUP BY user_id
        
        UNION ALL
        
        SELECT SUM(total_fare) as total 
        FROM train_bookings 
        WHERE booking_status = 'Confirmed'
        GROUP BY user_id
        
        UNION ALL
        
        SELECT SUM(total_fare) as total 
        FROM flight_bookings 
        WHERE booking_status = 'Confirmed'
        GROUP BY user_id
    ) as avg_expenses
)
ORDER BY total_expense DESC;

-- ============================================================
-- 2. MOST POPULAR ROUTE PER TRANSPORT MODE
-- ============================================================
-- Subquery: Use ROW_NUMBER to find top route in each category

SELECT booking_type, route, booking_count, total_revenue
FROM (
    -- KSRTC Routes
    SELECT 
        'KSRTC' as booking_type,
        CONCAT(r.origin, ' → ', r.destination) as route,
        COUNT(kb.booking_id) as booking_count,
        SUM(kb.total_fare) as total_revenue,
        ROW_NUMBER() OVER (PARTITION BY 'KSRTC' ORDER BY COUNT(kb.booking_id) DESC) as rn
    FROM ksrtc_bookings kb
    JOIN ksrtc_schedules s ON kb.schedule_id = s.schedule_id
    JOIN ksrtc_routes r ON s.route_id = r.route_id
    WHERE kb.booking_status = 'Confirmed'
    GROUP BY r.route_id, r.origin, r.destination
    
    UNION ALL
    
    -- Train Routes
    SELECT 
        'Train' as booking_type,
        CONCAT(source_station, ' → ', destination_station) as route,
        COUNT(booking_id) as booking_count,
        SUM(total_fare) as total_revenue,
        ROW_NUMBER() OVER (PARTITION BY 'Train' ORDER BY COUNT(booking_id) DESC) as rn
    FROM train_bookings
    WHERE booking_status = 'Confirmed'
    GROUP BY source_station, destination_station
    
    UNION ALL
    
    -- Flight Routes
    SELECT 
        'Flight' as booking_type,
        CONCAT(ap1.city, ' → ', ap2.city) as route,
        COUNT(fb.booking_id) as booking_count,
        SUM(fb.total_fare) as total_revenue,
        ROW_NUMBER() OVER (PARTITION BY 'Flight' ORDER BY COUNT(fb.booking_id) DESC) as rn
    FROM flight_bookings fb
    JOIN flights f ON fb.flight_id = f.flight_id
    JOIN airports ap1 ON f.origin_code = ap1.airport_code
    JOIN airports ap2 ON f.destination_code = ap2.airport_code
    WHERE fb.booking_status = 'Confirmed'
    GROUP BY f.origin_code, f.destination_code, ap1.city, ap2.city
) as ranked_routes
WHERE rn = 1;

-- ============================================================
-- 3. FIND BUSES WITH ABOVE AVERAGE BOOKINGS
-- ============================================================
-- Subquery: Filter buses based on average booking count

SELECT 
    b.bus_number,
    b.bus_type,
    (
        SELECT COUNT(*) 
        FROM ksrtc_bookings kb 
        JOIN ksrtc_schedules s ON kb.schedule_id = s.schedule_id
        WHERE s.bus_id = b.bus_id AND kb.booking_status = 'Confirmed'
    ) as total_bookings,
    (
        SELECT SUM(kb.total_fare) 
        FROM ksrtc_bookings kb 
        JOIN ksrtc_schedules s ON kb.schedule_id = s.schedule_id
        WHERE s.bus_id = b.bus_id AND kb.booking_status = 'Confirmed'
    ) as total_revenue
FROM ksrtc_buses b
WHERE (
    SELECT COUNT(*) 
    FROM ksrtc_bookings kb 
    JOIN ksrtc_schedules s ON kb.schedule_id = s.schedule_id
    WHERE s.bus_id = b.bus_id AND kb.booking_status = 'Confirmed'
) > (
    -- Average bookings per bus
    SELECT AVG(booking_count) FROM (
        SELECT COUNT(*) as booking_count
        FROM ksrtc_bookings kb
        JOIN ksrtc_schedules s ON kb.schedule_id = s.schedule_id
        WHERE kb.booking_status = 'Confirmed'
        GROUP BY s.bus_id
    ) as bus_bookings
)
ORDER BY total_bookings DESC;

-- ============================================================
-- 4. USERS WITH NO BOOKINGS IN LAST 30 DAYS
-- ============================================================
-- Subquery: Find users without recent activity

SELECT 
    u.user_id,
    u.username,
    u.email,
    u.last_login,
    (
        SELECT MAX(booking_time) FROM (
            SELECT booking_time FROM ksrtc_bookings WHERE user_id = u.user_id
            UNION ALL
            SELECT booking_time FROM train_bookings WHERE user_id = u.user_id
            UNION ALL
            SELECT booking_time FROM flight_bookings WHERE user_id = u.user_id
        ) as all_bookings
    ) as last_booking_date
FROM users u
WHERE u.user_type = 'user'
AND NOT EXISTS (
    SELECT 1 FROM ksrtc_bookings kb 
    WHERE kb.user_id = u.user_id 
    AND kb.booking_time >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
)
AND NOT EXISTS (
    SELECT 1 FROM train_bookings tb 
    WHERE tb.user_id = u.user_id 
    AND tb.booking_time >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
)
AND NOT EXISTS (
    SELECT 1 FROM flight_bookings fb 
    WHERE fb.user_id = u.user_id 
    AND fb.booking_time >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
)
ORDER BY last_booking_date DESC;

-- ============================================================
-- 5. TRAINS WITH HIGHEST REVENUE PER KM
-- ============================================================
-- Subquery: Calculate revenue efficiency

SELECT 
    t.train_number,
    t.train_name,
    (
        SELECT SUM(tb.total_fare) 
        FROM train_bookings tb 
        WHERE tb.train_id = t.train_id AND tb.booking_status = 'Confirmed'
    ) as total_revenue,
    (
        SELECT AVG(ts.distance_km) 
        FROM train_schedules ts 
        WHERE ts.train_id = t.train_id
    ) as avg_distance_km,
    (
        SELECT SUM(tb.total_fare) / AVG(ts.distance_km)
        FROM train_bookings tb, train_schedules ts
        WHERE tb.train_id = t.train_id 
        AND ts.train_id = t.train_id 
        AND tb.booking_status = 'Confirmed'
    ) as revenue_per_km
FROM trains t
WHERE (
    SELECT COUNT(*) 
    FROM train_bookings tb 
    WHERE tb.train_id = t.train_id AND tb.booking_status = 'Confirmed'
) > 0
ORDER BY revenue_per_km DESC
LIMIT 10;

-- ============================================================
-- 6. FLIGHTS WITH SEATS BOOKED PERCENTAGE
-- ============================================================
-- Subquery: Calculate occupancy rate

SELECT 
    f.flight_number,
    a.airline_name,
    ap1.city as origin,
    ap2.city as destination,
    f.total_seats,
    (
        SELECT COUNT(*) 
        FROM flight_seats fs 
        WHERE fs.flight_id = f.flight_id AND fs.is_available = FALSE
    ) as booked_seats,
    ROUND(
        (SELECT COUNT(*) FROM flight_seats fs WHERE fs.flight_id = f.flight_id AND fs.is_available = FALSE) 
        * 100.0 / f.total_seats, 2
    ) as occupancy_percent,
    (
        SELECT SUM(fb.total_fare) 
        FROM flight_bookings fb 
        WHERE fb.flight_id = f.flight_id AND fb.booking_status = 'Confirmed'
    ) as total_revenue
FROM flights f
JOIN airlines a ON f.airline_id = a.airline_id
JOIN airports ap1 ON f.origin_code = ap1.airport_code
JOIN airports ap2 ON f.destination_code = ap2.airport_code
WHERE (
    SELECT COUNT(*) 
    FROM flight_bookings fb 
    WHERE fb.flight_id = f.flight_id
) > 0
ORDER BY occupancy_percent DESC;

-- ============================================================
-- 7. ROUTES WITH HIGHER THAN AVERAGE CANCELLATION RATE
-- ============================================================
-- Subquery: Find problematic routes

SELECT 
    route_info.route_name,
    route_info.total_bookings,
    route_info.cancelled_bookings,
    ROUND(route_info.cancelled_bookings * 100.0 / route_info.total_bookings, 2) as cancellation_rate
FROM (
    SELECT 
        r.route_name,
        r.origin,
        r.destination,
        COUNT(kb.booking_id) as total_bookings,
        COUNT(CASE WHEN kb.booking_status = 'Cancelled' THEN 1 END) as cancelled_bookings
    FROM ksrtc_routes r
    JOIN ksrtc_schedules s ON r.route_id = s.route_id
    JOIN ksrtc_bookings kb ON s.schedule_id = kb.schedule_id
    GROUP BY r.route_id, r.route_name, r.origin, r.destination
    HAVING total_bookings > 5
) as route_info
WHERE (route_info.cancelled_bookings * 100.0 / route_info.total_bookings) > (
    -- Calculate average cancellation rate
    SELECT AVG(cancel_rate) FROM (
        SELECT 
            (COUNT(CASE WHEN booking_status = 'Cancelled' THEN 1 END) * 100.0 / COUNT(*)) as cancel_rate
        FROM ksrtc_bookings
        GROUP BY schedule_id
        HAVING COUNT(*) > 5
    ) as avg_rates
)
ORDER BY cancellation_rate DESC;

-- ============================================================
-- 8. USERS WHO BOOKED ALL THREE TRANSPORT MODES
-- ============================================================
-- Subquery: Find multi-modal travelers

SELECT 
    u.user_id,
    u.username,
    u.email,
    (SELECT COUNT(*) FROM ksrtc_bookings WHERE user_id = u.user_id) as ksrtc_count,
    (SELECT COUNT(*) FROM train_bookings WHERE user_id = u.user_id) as train_count,
    (SELECT COUNT(*) FROM flight_bookings WHERE user_id = u.user_id) as flight_count,
    (
        SELECT SUM(fare) FROM (
            SELECT total_fare as fare FROM ksrtc_bookings WHERE user_id = u.user_id AND booking_status = 'Confirmed'
            UNION ALL
            SELECT total_fare FROM train_bookings WHERE user_id = u.user_id AND booking_status = 'Confirmed'
            UNION ALL
            SELECT total_fare FROM flight_bookings WHERE user_id = u.user_id AND booking_status = 'Confirmed'
        ) as all_fares
    ) as total_spent
FROM users u
WHERE EXISTS (
    SELECT 1 FROM ksrtc_bookings WHERE user_id = u.user_id
)
AND EXISTS (
    SELECT 1 FROM train_bookings WHERE user_id = u.user_id
)
AND EXISTS (
    SELECT 1 FROM flight_bookings WHERE user_id = u.user_id
)
ORDER BY total_spent DESC;

-- ============================================================
-- 9. PEAK BOOKING DAY FOR EACH MONTH
-- ============================================================
-- Subquery: Find busiest day per month

SELECT 
    month_year,
    booking_date,
    bookings_count
FROM (
    SELECT 
        DATE_FORMAT(booking_date, '%Y-%m') as month_year,
        booking_date,
        booking_count as bookings_count,
        ROW_NUMBER() OVER (PARTITION BY DATE_FORMAT(booking_date, '%Y-%m') ORDER BY booking_count DESC) as rn
    FROM (
        SELECT 
            DATE(booking_time) as booking_date,
            COUNT(*) as booking_count
        FROM (
            SELECT booking_time FROM ksrtc_bookings
            UNION ALL
            SELECT booking_time FROM train_bookings
            UNION ALL
            SELECT booking_time FROM flight_bookings
        ) as all_bookings
        GROUP BY DATE(booking_time)
    ) as daily_counts
) as ranked_days
WHERE rn = 1
ORDER BY month_year DESC
LIMIT 12;

-- ============================================================
-- 10. USERS WITH HIGHEST AVERAGE BOOKING VALUE
-- ============================================================
-- Subquery: Find premium customers

SELECT 
    u.username,
    u.email,
    booking_stats.total_bookings,
    booking_stats.total_spent,
    booking_stats.avg_booking_value
FROM users u
JOIN (
    SELECT 
        user_id,
        COUNT(*) as total_bookings,
        SUM(fare) as total_spent,
        AVG(fare) as avg_booking_value
    FROM (
        SELECT user_id, total_fare as fare FROM ksrtc_bookings WHERE booking_status = 'Confirmed'
        UNION ALL
        SELECT user_id, total_fare FROM train_bookings WHERE booking_status = 'Confirmed'
        UNION ALL
        SELECT user_id, total_fare FROM flight_bookings WHERE booking_status = 'Confirmed'
    ) as all_bookings
    GROUP BY user_id
    HAVING total_bookings >= 3
) as booking_stats ON u.user_id = booking_stats.user_id
WHERE booking_stats.avg_booking_value > (
    -- Calculate overall average booking value
    SELECT AVG(fare) FROM (
        SELECT total_fare as fare FROM ksrtc_bookings WHERE booking_status = 'Confirmed'
        UNION ALL
        SELECT total_fare FROM train_bookings WHERE booking_status = 'Confirmed'
        UNION ALL
        SELECT total_fare FROM flight_bookings WHERE booking_status = 'Confirmed'
    ) as all_fares
)
ORDER BY booking_stats.avg_booking_value DESC;

-- ============================================================
-- END OF NESTED QUERIES
-- ============================================================
