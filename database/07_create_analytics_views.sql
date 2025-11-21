-- Create Views for Admin Analytics Dashboard
-- Views to aggregate user behavior and preferences

USE transport_system;

-- View 1: Transport Mode Usage Statistics
DROP VIEW IF EXISTS v_transport_mode_stats;
CREATE VIEW v_transport_mode_stats AS
SELECT 
    transport_mode,
    COUNT(*) as search_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM route_searches), 2) as percentage
FROM route_searches
GROUP BY transport_mode
ORDER BY search_count DESC;

-- View 2: Popular Routes
DROP VIEW IF EXISTS v_popular_routes;
CREATE VIEW v_popular_routes AS
SELECT 
    source_location,
    destination_location,
    COUNT(*) as search_count,
    transport_mode
FROM route_searches
GROUP BY source_location, destination_location, transport_mode
ORDER BY search_count DESC
LIMIT 20;

-- View 3: Private Mode Preferences
DROP VIEW IF EXISTS v_private_mode_preferences;
CREATE VIEW v_private_mode_preferences AS
SELECT 
    private_mode,
    COUNT(*) as usage_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transport_preferences WHERE private_mode IS NOT NULL), 2) as percentage
FROM transport_preferences
WHERE private_mode IS NOT NULL
GROUP BY private_mode
ORDER BY usage_count DESC;

-- View 4: Public Mode Preferences
DROP VIEW IF EXISTS v_public_mode_preferences;
CREATE VIEW v_public_mode_preferences AS
SELECT 
    public_mode,
    COUNT(*) as usage_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transport_preferences WHERE public_mode IS NOT NULL), 2) as percentage
FROM transport_preferences
WHERE public_mode IS NOT NULL
GROUP BY public_mode
ORDER BY usage_count DESC;

-- View 5: Multi-Modal Type Distribution
DROP VIEW IF EXISTS v_multi_modal_distribution;
CREATE VIEW v_multi_modal_distribution AS
SELECT 
    multi_modal_type,
    COUNT(*) as usage_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transport_preferences WHERE multi_modal_type IS NOT NULL), 2) as percentage
FROM transport_preferences
WHERE multi_modal_type IS NOT NULL
GROUP BY multi_modal_type
ORDER BY usage_count DESC;

-- View 6: Booking Statistics by Type
DROP VIEW IF EXISTS v_booking_stats;
CREATE VIEW v_booking_stats AS
SELECT 
    booking_type,
    COUNT(*) as total_bookings,
    SUM(CASE WHEN booking_status = 'confirmed' THEN 1 ELSE 0 END) as confirmed_bookings,
    SUM(CASE WHEN booking_status = 'cancelled' THEN 1 ELSE 0 END) as cancelled_bookings,
    ROUND(AVG(fare_amount), 2) as avg_fare
FROM bookings
GROUP BY booking_type
ORDER BY total_bookings DESC;

-- View 7: User Activity Summary
DROP VIEW IF EXISTS v_user_activity;
CREATE VIEW v_user_activity AS
SELECT 
    u.user_id,
    u.username,
    u.full_name,
    COUNT(DISTINCT rs.search_id) as total_searches,
    COUNT(DISTINCT b.booking_id) as total_bookings,
    MAX(rs.search_timestamp) as last_search_date
FROM users u
LEFT JOIN route_searches rs ON u.user_id = rs.user_id
LEFT JOIN bookings b ON u.user_id = b.user_id
WHERE u.user_type = 'user'
GROUP BY u.user_id, u.username, u.full_name
ORDER BY total_searches DESC;

-- View 8: Route Optimization Preference Stats
DROP VIEW IF EXISTS v_optimization_preferences;
CREATE VIEW v_optimization_preferences AS
SELECT 
    preference_type,
    COUNT(*) as preference_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transport_preferences), 2) as percentage
FROM transport_preferences
GROUP BY preference_type
ORDER BY preference_count DESC;

SELECT 'Analytics views created successfully!' AS Status;
