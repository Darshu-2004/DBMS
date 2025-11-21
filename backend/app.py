"""
Multi-Modal Transport System - Backend API
Flask application with REST APIs for user authentication, route search, bookings, and admin analytics
"""

from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS
import bcrypt
import jwt
import datetime
from functools import wraps
import os
from dotenv import load_dotenv
from database import execute_query, execute_query_one, test_connection

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')
app.config['JWT_SECRET'] = os.getenv('JWT_SECRET', 'jwt_secret_key')

# Enable CORS for all routes
CORS(app)

# JWT token decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token is missing!', 'success': False}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Allow test token for development
            if token == 'test-token':
                current_user = {
                    'user_id': 3,
                    'username': 'Test User',
                    'email': 'test@test.com',
                    'user_type': 'user'
                }
            else:
                data = jwt.decode(token, app.config['JWT_SECRET'], algorithms=['HS256'])
                current_user = execute_query_one(
                    "SELECT user_id, username, email, user_type FROM users WHERE user_id = %s",
                    (data['user_id'],)
                )
                
                if not current_user:
                    return jsonify({'message': 'Invalid token!', 'success': False}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!', 'success': False}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!', 'success': False}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated


# Admin only decorator
def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user['user_type'] != 'admin':
            return jsonify({'message': 'Admin access required!', 'success': False}), 403
        return f(current_user, *args, **kwargs)
    return decorated


# Page authentication helper
def check_page_auth():
    """Check if user has valid token for accessing protected pages"""
    token = request.cookies.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return False
    try:
        jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return True
    except:
        return False


# ========== FRONTEND ROUTES ==========
@app.route('/')
def index():
    """Serve main index page"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/signin.html')
def signin_page():
    """Serve signin page"""
    return send_from_directory(app.static_folder, 'signin.html')

@app.route('/signup.html')
def signup_page():
    """Serve signup page"""
    return send_from_directory(app.static_folder, 'signup.html')

@app.route('/admin.html')
def admin_page():
    """Serve admin dashboard page"""
    return send_from_directory(app.static_folder, 'admin.html')

@app.route('/admin_login.html')
def admin_login_page():
    """Serve admin login page"""
    return send_from_directory(app.static_folder, 'admin_login.html')

@app.route('/ksrtc.html')
def ksrtc_page():
    """Serve KSRTC booking page"""
    return send_from_directory(app.static_folder, 'ksrtc.html')

@app.route('/mobile_tickets.html')
def mobile_tickets_page():
    """Serve mobile tickets page"""
    return send_from_directory(app.static_folder, 'mobile_tickets.html')

@app.route('/expenses.html')
def expenses_page():
    """Serve expenses page"""
    return send_from_directory(app.static_folder, 'expenses.html')


# ========== HEALTH CHECK ==========
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    db_status = test_connection()
    return jsonify({
        'status': 'running',
        'database': 'connected' if db_status else 'disconnected',
        'timestamp': datetime.datetime.now().isoformat()
    })


# ========== AUTHENTICATION ENDPOINTS ==========

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'full_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'message': f'{field} is required', 'success': False}), 400
        
        # Check if user already exists
        existing_user = execute_query_one(
            "SELECT user_id FROM users WHERE username = %s OR email = %s",
            (data['username'], data['email'])
        )
        
        if existing_user:
            return jsonify({'message': 'Username or email already exists', 'success': False}), 409
        
        # Hash password
        password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insert user
        user_id = execute_query(
            """INSERT INTO users (username, email, password_hash, full_name, phone_number) 
               VALUES (%s, %s, %s, %s, %s)""",
            (data['username'], data['email'], password_hash, data['full_name'], 
             data.get('phone_number'))
        )
        
        if user_id:
            return jsonify({
                'message': 'User registered successfully',
                'success': True,
                'user_id': user_id
            }), 201
        else:
            return jsonify({'message': 'Registration failed', 'success': False}), 500
            
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}', 'success': False}), 500


@app.route('/api/auth/signin', methods=['POST'])
def signin():
    """User login endpoint"""
    try:
        data = request.json
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Username and password required', 'success': False}), 400
        
        # Get user
        user = execute_query_one(
            "SELECT user_id, username, email, password_hash, full_name, user_type FROM users WHERE username = %s OR email = %s",
            (data['username'], data['username'])
        )
        
        if not user:
            return jsonify({'message': 'Invalid credentials', 'success': False}), 401
        
        # Verify password
        if not bcrypt.checkpw(data['password'].encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({'message': 'Invalid credentials', 'success': False}), 401
        
        # Update last login
        execute_query("UPDATE users SET last_login = NOW() WHERE user_id = %s", (user['user_id'],))
        
        # Generate JWT token
        token = jwt.encode({
            'user_id': user['user_id'],
            'username': user['username'],
            'user_type': user['user_type'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, app.config['JWT_SECRET'], algorithm='HS256')
        
        return jsonify({
            'message': 'Login successful',
            'success': True,
            'token': token,
            'user': {
                'user_id': user['user_id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name'],
                'user_type': user['user_type']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}', 'success': False}), 500


# ========== ROUTE SEARCH ENDPOINTS ==========

@app.route('/api/routes/search', methods=['POST'])
@token_required
def search_routes(current_user):
    """Search routes and save search history"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('source') or not data.get('destination') or not data.get('transport_mode'):
            return jsonify({'message': 'Source, destination, and transport mode required', 'success': False}), 400
        
        # Insert route search
        search_id = execute_query(
            """INSERT INTO route_searches (user_id, source_location, destination_location, transport_mode) 
               VALUES (%s, %s, %s, %s)""",
            (current_user['user_id'], data['source'], data['destination'], data['transport_mode'])
        )
        
        # Insert transport preferences if provided
        if search_id and (data.get('private_mode') or data.get('public_mode') or data.get('multi_modal_type')):
            execute_query(
                """INSERT INTO transport_preferences 
                   (search_id, user_id, private_mode, public_mode, multi_modal_type, preference_type) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (search_id, current_user['user_id'], data.get('private_mode'), 
                 data.get('public_mode'), data.get('multi_modal_type'), 
                 data.get('preference_type', 'time'))
            )
        
        return jsonify({
            'message': 'Route search saved successfully',
            'success': True,
            'search_id': search_id,
            'routes': generate_mock_routes(data)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}', 'success': False}), 500


def generate_mock_routes(search_data):
    """Generate mock route results with coordinates for mapping"""
    base_routes = []
    
    mode = search_data.get('transport_mode')
    source = search_data.get('source', '')
    dest = search_data.get('destination', '')
    
    # Bangalore coordinates (mock data - replace with geocoding later)
    coords_map = {
        'koramangala': {'lat': 12.9352, 'lng': 77.6245},
        'mg road': {'lat': 12.9716, 'lng': 77.5946},
        'whitefield': {'lat': 12.9698, 'lng': 77.7500},
        'hsr layout': {'lat': 12.9121, 'lng': 77.6446},
        'indiranagar': {'lat': 12.9719, 'lng': 77.6412},
        'jayanagar': {'lat': 12.9250, 'lng': 77.5838},
        'marathahalli': {'lat': 13.0104, 'lng': 77.6976},
        'electronic city': {'lat': 12.8395, 'lng': 77.6770}
    }
    
    # Try to find coordinates
    source_lower = source.lower()
    dest_lower = dest.lower()
    
    source_coords = None
    dest_coords = None
    
    for key, coords in coords_map.items():
        if key in source_lower:
            source_coords = coords
        if key in dest_lower:
            dest_coords = coords
    
    # Default to Bangalore center if not found
    if not source_coords:
        source_coords = {'lat': 12.9716, 'lng': 77.5946}
    if not dest_coords:
        dest_coords = {'lat': 12.9352, 'lng': 77.6245}
    
    # Calculate distance (simple haversine)
    import math
    R = 6371  # Earth's radius in km
    
    lat1, lon1 = math.radians(source_coords['lat']), math.radians(source_coords['lng'])
    lat2, lon2 = math.radians(dest_coords['lat']), math.radians(dest_coords['lng'])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    distance_km = R * c
    
    if mode == 'private' or mode == 'multi-modal':
        private_type = search_data.get('private_mode', 'car')
        
        # Calculate based on mode
        speeds = {'bike': 40, 'car': 35, 'walk': 5}
        fuel_rates = {'bike': 3.5, 'car': 8.0, 'walk': 0}
        fuel_price = 100  # per liter
        
        speed = speeds.get(private_type, 35)
        duration_mins = (distance_km / speed) * 60
        fuel_consumed = (distance_km / 100) * fuel_rates.get(private_type, 0)
        fuel_cost = fuel_consumed * fuel_price
        
        base_routes.append({
            'id': 1,
            'type': 'private',
            'mode': private_type,
            'duration': f'{int(duration_mins)} mins',
            'distance': f'{distance_km:.1f} km',
            'cost': 'Free' if private_type == 'walk' else f'₹{int(fuel_cost)}',
            'fuel_cost': f'₹{int(fuel_cost)}' if private_type != 'walk' else None,
            'eta': f'{int(duration_mins)} mins',
            'source_coords': source_coords,
            'dest_coords': dest_coords,
            'distance_km': distance_km,
            'duration_mins': duration_mins,
            'speed_kmh': speed
        })
    
    if mode == 'public' or mode == 'multi-modal':
        public_type = search_data.get('public_mode', 'metro')
        
        speeds = {'bmtc': 25, 'metro': 45, 'aggregator': 30}
        costs = {'bmtc': 25, 'metro': 40, 'aggregator': int(distance_km * 15)}
        
        speed = speeds.get(public_type, 30)
        duration_mins = (distance_km / speed) * 60
        
        base_routes.append({
            'id': 2,
            'type': 'public',
            'mode': public_type,
            'duration': f'{int(duration_mins)} mins',
            'distance': f'{distance_km:.1f} km',
            'cost': f'₹{costs.get(public_type, 30)}',
            'eta': f'{int(duration_mins)} mins',
            'source_coords': source_coords,
            'dest_coords': dest_coords,
            'distance_km': distance_km,
            'duration_mins': duration_mins,
            'speed_kmh': speed
        })
    
    return base_routes


@app.route('/api/routes/history', methods=['GET'])
@token_required
def get_route_history(current_user):
    """Get user's route search history"""
    try:
        history = execute_query(
            """SELECT rs.*, tp.private_mode, tp.public_mode, tp.multi_modal_type, tp.preference_type
               FROM route_searches rs
               LEFT JOIN transport_preferences tp ON rs.search_id = tp.search_id
               WHERE rs.user_id = %s
               ORDER BY rs.search_timestamp DESC
               LIMIT 50""",
            (current_user['user_id'],),
            fetch=True
        )
        
        return jsonify({
            'success': True,
            'history': history or []
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}', 'success': False}), 500


# ========== BOOKING ENDPOINTS ==========

@app.route('/api/bookings/create', methods=['POST'])
@token_required
def create_booking(current_user):
    """Create a new booking"""
    try:
        data = request.json
        
        # Validate required fields
        required = ['booking_type', 'source', 'destination', 'journey_date']
        for field in required:
            if field not in data:
                return jsonify({'message': f'{field} is required', 'success': False}), 400
        
        # Generate booking reference
        import random
        booking_ref = f"TRP{random.randint(100000, 999999)}"
        
        # Insert booking
        booking_id = execute_query(
            """INSERT INTO bookings 
               (user_id, booking_type, source, destination, booking_date, booking_time, 
                journey_date, journey_time, passenger_count, fare_amount, booking_status, booking_reference) 
               VALUES (%s, %s, %s, %s, CURDATE(), CURTIME(), %s, %s, %s, %s, 'confirmed', %s)""",
            (current_user['user_id'], data['booking_type'], data['source'], data['destination'],
             data['journey_date'], data.get('journey_time'), data.get('passenger_count', 1),
             data.get('fare_amount'), booking_ref)
        )
        
        if booking_id:
            return jsonify({
                'message': 'Booking created successfully',
                'success': True,
                'booking_id': booking_id,
                'booking_reference': booking_ref
            }), 201
        else:
            return jsonify({'message': 'Booking failed', 'success': False}), 500
            
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}', 'success': False}), 500


@app.route('/api/bookings/my-bookings', methods=['GET'])
@token_required
def get_my_bookings(current_user):
    """Get user's bookings"""
    try:
        bookings = execute_query(
            """SELECT * FROM bookings 
               WHERE user_id = %s 
               ORDER BY created_at DESC 
               LIMIT 50""",
            (current_user['user_id'],),
            fetch=True
        )
        
        return jsonify({
            'success': True,
            'bookings': bookings or []
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}', 'success': False}), 500


@app.route('/api/bookings/track/<int:booking_id>', methods=['GET'])
@token_required
def track_booking(current_user, booking_id):
    """Get live tracking information for a booking"""
    try:
        tracking = execute_query_one(
            """SELECT lt.*, b.source, b.destination, b.booking_type
               FROM live_tracking lt
               JOIN bookings b ON lt.booking_id = b.booking_id
               WHERE lt.booking_id = %s AND b.user_id = %s""",
            (booking_id, current_user['user_id'])
        )
        
        if tracking:
            return jsonify({
                'success': True,
                'tracking': tracking
            }), 200
        else:
            # Return mock tracking data if not found
            return jsonify({
                'success': True,
                'tracking': {
                    'booking_id': booking_id,
                    'status': 'scheduled',
                    'estimated_arrival': '11:30 AM',
                    'distance_remaining': 8.5
                }
            }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}', 'success': False}), 500


# ========== LIVE NAVIGATION ENDPOINTS ==========

@app.route('/api/navigation/start', methods=['POST'])
@token_required
def start_navigation(current_user):
    """Start live navigation tracking"""
    try:
        data = request.json
        
        # Create a tracking session
        tracking_id = execute_query(
            """INSERT INTO live_tracking 
               (booking_id, user_id, vehicle_number, current_location, 
                latitude, longitude, distance_remaining, status) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, 'in-transit')""",
            (data.get('booking_id', 0), current_user['user_id'], 
             data.get('vehicle_number', 'N/A'), data.get('source'),
             data.get('source_lat'), data.get('source_lng'),
             data.get('total_distance'))
        )
        
        return jsonify({
            'success': True,
            'tracking_id': tracking_id,
            'message': 'Navigation started'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}', 'success': False}), 500


@app.route('/api/navigation/update', methods=['POST'])
@token_required
def update_navigation(current_user):
    """Update navigation position"""
    try:
        data = request.json
        
        execute_query(
            """UPDATE live_tracking 
               SET latitude = %s, longitude = %s, 
                   distance_remaining = %s, current_location = %s,
                   last_updated = NOW()
               WHERE tracking_id = %s AND user_id = %s""",
            (data.get('lat'), data.get('lng'), 
             data.get('distance_remaining'), data.get('location'),
             data.get('tracking_id'), current_user['user_id'])
        )
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}', 'success': False}), 500


@app.route('/api/navigation/stop', methods=['POST'])
@token_required
def stop_navigation(current_user):
    """Stop navigation tracking"""
    try:
        data = request.json
        
        execute_query(
            """UPDATE live_tracking 
               SET status = 'arrived', last_updated = NOW()
               WHERE tracking_id = %s AND user_id = %s""",
            (data.get('tracking_id'), current_user['user_id'])
        )
        
        return jsonify({
            'success': True,
            'message': 'Navigation stopped'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}', 'success': False}), 500


# ========== ADMIN ANALYTICS ENDPOINTS ==========

@app.route('/api/admin/stats/transport-modes', methods=['GET'])
@token_required
@admin_required
def get_transport_mode_stats(current_user):
    """Get transport mode usage statistics"""
    try:
        stats = execute_query("SELECT * FROM v_transport_mode_stats", fetch=True)
        return jsonify({'success': True, 'stats': stats or []}), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}', 'success': False}), 500


@app.route('/api/admin/stats/popular-routes', methods=['GET'])
@token_required
@admin_required
def get_popular_routes(current_user):
    """Get popular routes"""
    try:
        routes = execute_query("SELECT * FROM v_popular_routes", fetch=True)
        return jsonify({'success': True, 'routes': routes or []}), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}', 'success': False}), 500


@app.route('/api/admin/stats/private-mode', methods=['GET'])
@token_required
@admin_required
def get_private_mode_stats(current_user):
    """Get private mode preferences"""
    try:
        stats = execute_query("SELECT * FROM v_private_mode_preferences", fetch=True)
        return jsonify({'success': True, 'stats': stats or []}), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}', 'success': False}), 500


@app.route('/api/admin/stats/public-mode', methods=['GET'])
@token_required
@admin_required
def get_public_mode_stats(current_user):
    """Get public mode preferences"""
    try:
        stats = execute_query("SELECT * FROM v_public_mode_preferences", fetch=True)
        return jsonify({'success': True, 'stats': stats or []}), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}', 'success': False}), 500


@app.route('/api/admin/stats/multi-modal', methods=['GET'])
@token_required
@admin_required
def get_multi_modal_stats(current_user):
    """Get multi-modal type distribution"""
    try:
        stats = execute_query("SELECT * FROM v_multi_modal_distribution", fetch=True)
        return jsonify({'success': True, 'stats': stats or []}), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}', 'success': False}), 500


@app.route('/api/admin/stats/bookings', methods=['GET'])
@token_required
@admin_required
def get_booking_stats(current_user):
    """Get booking statistics"""
    try:
        stats = execute_query("SELECT * FROM v_booking_stats", fetch=True)
        return jsonify({'success': True, 'stats': stats or []}), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}', 'success': False}), 500


@app.route('/api/admin/stats/users', methods=['GET'])
@token_required
@admin_required
def get_user_activity_stats(current_user):
    """Get user activity summary"""
    try:
        stats = execute_query("SELECT * FROM v_user_activity", fetch=True)
        return jsonify({'success': True, 'stats': stats or []}), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}', 'success': False}), 500


@app.route('/api/admin/stats/optimization', methods=['GET'])
@token_required
@admin_required
def get_optimization_stats(current_user):
    """Get route optimization preferences"""
    try:
        stats = execute_query("SELECT * FROM v_optimization_preferences", fetch=True)
        return jsonify({'success': True, 'stats': stats or []}), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}', 'success': False}), 500


@app.route('/api/admin/dashboard', methods=['GET'])
@token_required
def get_admin_dashboard(current_user):
    """Get dashboard data - shows all data for admins, user-specific data for regular users"""
    try:
        is_admin = current_user.get('user_type') == 'admin'
        
        if is_admin:
            # Admin sees all data
            dashboard_data = {
                # Original search analytics
                'transport_modes': execute_query("SELECT * FROM v_transport_mode_stats", fetch=True) or [],
                'popular_routes': execute_query("SELECT * FROM v_popular_routes LIMIT 10", fetch=True) or [],
                'private_mode': execute_query("SELECT * FROM v_private_mode_preferences", fetch=True) or [],
                'public_mode': execute_query("SELECT * FROM v_public_mode_preferences", fetch=True) or [],
                'multi_modal': execute_query("SELECT * FROM v_multi_modal_distribution", fetch=True) or [],
                'bookings': execute_query("SELECT * FROM v_booking_stats", fetch=True) or [],
                'user_activity': execute_query("SELECT * FROM v_user_activity LIMIT 20", fetch=True) or [],
                'optimization': execute_query("SELECT * FROM v_optimization_preferences", fetch=True) or [],
                
                # Booking system analytics
                'all_bookings': execute_query("SELECT * FROM v_all_booking_stats", fetch=True) or [],
                'ksrtc_stats': execute_query("SELECT * FROM v_ksrtc_booking_stats", fetch=True) or [],
                'train_stats': execute_query("SELECT * FROM v_train_booking_stats", fetch=True) or [],
                'flight_stats': execute_query("SELECT * FROM v_flight_booking_stats", fetch=True) or [],
                'popular_train_routes': execute_query("SELECT * FROM v_popular_train_routes", fetch=True) or [],
                'popular_flight_routes': execute_query("SELECT * FROM v_popular_flight_routes", fetch=True) or [],
                'popular_ksrtc_routes': execute_query("SELECT * FROM v_popular_ksrtc_routes", fetch=True) or [],
                'user_expenses': execute_query("SELECT * FROM v_user_expense_summary LIMIT 20", fetch=True) or [],
                'daily_trends': execute_query("SELECT * FROM v_daily_booking_trends", fetch=True) or [],
                'peak_hours': execute_query("SELECT * FROM v_peak_booking_hours", fetch=True) or []
            }
        else:
            # Regular users see only their own data
            user_id = current_user['user_id']
            
            # Get user's booking stats with proper aggregation
            ksrtc_data = execute_query("""
                SELECT 
                    COUNT(*) as total_bookings, 
                    COALESCE(SUM(CASE WHEN booking_status = 'Confirmed' THEN 1 ELSE 0 END), 0) as confirmed_bookings,
                    COALESCE(SUM(CASE WHEN booking_status = 'Cancelled' THEN 1 ELSE 0 END), 0) as cancelled_bookings,
                    COALESCE(AVG(CASE WHEN booking_status = 'Confirmed' THEN total_fare END), 0) as avg_fare,
                    COALESCE(SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END), 0) as total_revenue
                FROM ksrtc_bookings WHERE user_id = %s
            """, (user_id,), fetch=True)
            
            train_data = execute_query("""
                SELECT 
                    COUNT(*) as total_bookings, 
                    COALESCE(SUM(CASE WHEN booking_status = 'Confirmed' THEN 1 ELSE 0 END), 0) as confirmed_bookings,
                    COALESCE(SUM(CASE WHEN booking_status = 'Cancelled' THEN 1 ELSE 0 END), 0) as cancelled_bookings,
                    COALESCE(AVG(CASE WHEN booking_status = 'Confirmed' THEN total_fare END), 0) as avg_fare,
                    COALESCE(SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END), 0) as total_revenue
                FROM train_bookings WHERE user_id = %s
            """, (user_id,), fetch=True)
            
            flight_data = execute_query("""
                SELECT 
                    COUNT(*) as total_bookings, 
                    COALESCE(SUM(CASE WHEN booking_status = 'Confirmed' THEN 1 ELSE 0 END), 0) as confirmed_bookings,
                    COALESCE(SUM(CASE WHEN booking_status = 'Cancelled' THEN 1 ELSE 0 END), 0) as cancelled_bookings,
                    COALESCE(AVG(CASE WHEN booking_status = 'Confirmed' THEN total_fare END), 0) as avg_fare,
                    COALESCE(SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END), 0) as total_revenue
                FROM flight_bookings WHERE user_id = %s
            """, (user_id,), fetch=True)
            
            # Get user's recent routes
            user_routes = execute_query("""
                SELECT 'KSRTC' as type, boarding_stop as source_location, destination_stop as destination_location, 
                       journey_date, total_fare, 'KSRTC' as transport_mode, 1 as search_count
                FROM ksrtc_bookings WHERE user_id = %s
                UNION ALL
                SELECT 'Train' as type, from_station as source_location, to_station as destination_location,
                       journey_date, total_fare, 'Train' as transport_mode, 1 as search_count
                FROM train_bookings WHERE user_id = %s
                UNION ALL
                SELECT 'Flight' as type, from_airport as source_location, to_airport as destination_location,
                       journey_date, total_fare, 'Flight' as transport_mode, 1 as search_count
                FROM flight_bookings WHERE user_id = %s
                ORDER BY journey_date DESC LIMIT 10
            """, (user_id, user_id, user_id), fetch=True) or []
            
            # Extract results
            ksrtc = ksrtc_data[0] if ksrtc_data else {'total_bookings': 0, 'confirmed_bookings': 0, 'cancelled_bookings': 0, 'avg_fare': 0, 'total_revenue': 0}
            train = train_data[0] if train_data else {'total_bookings': 0, 'confirmed_bookings': 0, 'cancelled_bookings': 0, 'avg_fare': 0, 'total_revenue': 0}
            flight = flight_data[0] if flight_data else {'total_bookings': 0, 'confirmed_bookings': 0, 'cancelled_bookings': 0, 'avg_fare': 0, 'total_revenue': 0}
            
            dashboard_data = {
                'user_mode': True,
                'transport_modes': [],
                'popular_routes': user_routes,
                'all_bookings': [
                    {
                        'transport_type': 'KSRTC',
                        'booking_type': 'KSRTC',
                        'total_bookings': int(ksrtc['total_bookings']),
                        'confirmed_bookings': int(ksrtc['confirmed_bookings']),
                        'cancelled_bookings': int(ksrtc['cancelled_bookings']),
                        'avg_fare': float(ksrtc['avg_fare']),
                        'total_revenue': float(ksrtc['total_revenue']),
                        'unique_users': 1 if ksrtc['total_bookings'] > 0 else 0
                    },
                    {
                        'transport_type': 'Train',
                        'booking_type': 'Train',
                        'total_bookings': int(train['total_bookings']),
                        'confirmed_bookings': int(train['confirmed_bookings']),
                        'cancelled_bookings': int(train['cancelled_bookings']),
                        'avg_fare': float(train['avg_fare']),
                        'total_revenue': float(train['total_revenue']),
                        'unique_users': 1 if train['total_bookings'] > 0 else 0
                    },
                    {
                        'transport_type': 'Flight',
                        'booking_type': 'Flight',
                        'total_bookings': int(flight['total_bookings']),
                        'confirmed_bookings': int(flight['confirmed_bookings']),
                        'cancelled_bookings': int(flight['cancelled_bookings']),
                        'avg_fare': float(flight['avg_fare']),
                        'total_revenue': float(flight['total_revenue']),
                        'unique_users': 1 if flight['total_bookings'] > 0 else 0
                    }
                ],
                'ksrtc_stats': [],
                'train_stats': [],
                'flight_stats': [],
                'user_activity': [],
                'bookings': [],
                'private_mode': [],
                'public_mode': [],
                'multi_modal': [],
                'optimization': [],
                'popular_train_routes': [],
                'popular_flight_routes': [],
                'popular_ksrtc_routes': [],
                'user_expenses': [],
                'daily_trends': [],
                'peak_hours': []
            }
        
        return jsonify({
            'success': True,
            'dashboard': dashboard_data
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}', 'success': False}), 500


# ========== KSRTC BOOKING ENDPOINTS ==========

@app.route('/api/ksrtc/stops', methods=['GET'])
def get_ksrtc_stops():
    """Get all KSRTC bus stops"""
    try:
        stops = execute_query(
            "SELECT stop_id, stop_name, city, is_major_stop FROM ksrtc_stops ORDER BY stop_name",
            fetch=True
        )
        
        if not stops:
            return jsonify({'success': True, 'stops': []})
        
        return jsonify({
            'success': True,
            'stops': [
                {
                    'stop_id': s['stop_id'],
                    'stop_name': s['stop_name'],
                    'city': s['city'],
                    'is_major_stop': bool(s['is_major_stop'])
                }
                for s in stops
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/ksrtc/search', methods=['GET'])
def search_ksrtc_buses():
    """Search available buses between stops"""
    try:
        from_stop = request.args.get('from')
        to_stop = request.args.get('to')
        journey_date = request.args.get('date')
        
        if not all([from_stop, to_stop, journey_date]):
            return jsonify({'success': False, 'message': 'Missing parameters'}), 400
        
        # Find routes and schedules
        buses = execute_query("""
            SELECT 
                s.schedule_id,
                r.route_number,
                r.source,
                r.destination,
                b.bus_id,
                b.bus_number,
                b.bus_type,
                b.total_seats,
                b.seater_seats,
                b.sleeper_seats,
                b.ac_available,
                s.departure_time,
                s.arrival_time,
                s.base_fare,
                s.status,
                (SELECT COUNT(*) FROM ksrtc_seats WHERE bus_id = b.bus_id AND is_available = TRUE) as available_seats
            FROM ksrtc_schedules s
            JOIN ksrtc_routes r ON s.route_id = r.route_id
            JOIN ksrtc_buses b ON s.bus_id = b.bus_id
            WHERE r.source = %s 
            AND r.destination = %s 
            AND s.status = 'Active'
            AND r.is_active = TRUE
            AND b.is_active = TRUE
            ORDER BY s.departure_time
        """, (from_stop, to_stop), fetch=True)
        
        if not buses:
            buses = []
        
        # Check seat availability for the journey date
        for bus in buses:
            booked_seats = execute_query_one("""
                SELECT COUNT(*) as booked_count
                FROM ksrtc_bookings
                WHERE schedule_id = %s 
                AND journey_date = %s 
                AND booking_status = 'Confirmed'
            """, (bus['schedule_id'], journey_date))
            
            bus['available_seats'] = bus['total_seats'] - (booked_seats['booked_count'] if booked_seats else 0)
            
            # Convert time objects to strings for JSON serialization
            if bus.get('departure_time'):
                bus['departure_time'] = str(bus['departure_time'])
            if bus.get('arrival_time'):
                bus['arrival_time'] = str(bus['arrival_time'])
        
        return jsonify({'success': True, 'buses': buses})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/ksrtc/seats', methods=['GET'])
def get_ksrtc_seats():
    """Get seat layout and availability"""
    try:
        schedule_id = request.args.get('schedule_id')
        journey_date = request.args.get('date')
        
        if not schedule_id or not journey_date:
            return jsonify({'success': False, 'message': 'Missing parameters'}), 400
        
        # Get bus_id from schedule
        schedule = execute_query_one(
            "SELECT bus_id FROM ksrtc_schedules WHERE schedule_id = %s",
            (schedule_id,)
        )
        
        if not schedule:
            return jsonify({'success': False, 'message': 'Schedule not found'}), 404
        
        # Get all seats for this bus
        seats = execute_query("""
            SELECT seat_id, seat_number, seat_type, seat_row, seat_column
            FROM ksrtc_seats
            WHERE bus_id = %s
            ORDER BY CAST(seat_number AS UNSIGNED)
        """, (schedule['bus_id'],), fetch=True)
        
        # Get booked seats for this schedule and date
        booked = execute_query("""
            SELECT seat_numbers
            FROM ksrtc_bookings
            WHERE schedule_id = %s 
            AND journey_date = %s
            AND booking_status = 'Confirmed'
        """, (schedule_id, journey_date), fetch=True)
        
        booked_seat_numbers = set()
        for booking in booked:
            booked_seat_numbers.update(booking['seat_numbers'].split(','))
        
        # Mark booked seats
        for seat in seats:
            seat['is_booked'] = seat['seat_number'] in booked_seat_numbers
        
        return jsonify({'success': True, 'seats': seats})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/ksrtc/book', methods=['POST'])
@token_required
def book_ksrtc_ticket(current_user):
    """Book KSRTC ticket"""
    try:
        data = request.json
        
        # Generate booking reference
        import random
        import string
        booking_ref = 'KSRTC' + ''.join(random.choices(string.digits, k=8))
        ticket_number = 'TKT' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        
        # Insert booking
        execute_query("""
            INSERT INTO ksrtc_bookings (
                user_id, schedule_id, booking_reference, passenger_name, passenger_age,
                passenger_gender, passenger_phone, passenger_email, boarding_stop,
                destination_stop, journey_date, seat_numbers, total_fare, booking_status,
                payment_status, payment_method
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            current_user['user_id'], data['schedule_id'], booking_ref,
            data['passenger_name'], data['passenger_age'], data['passenger_gender'],
            data['passenger_phone'], data['passenger_email'], data['boarding_stop'],
            data['destination_stop'], data['journey_date'], data['seat_numbers'],
            data['total_fare'], 'Confirmed', 'Paid', 'Online'
        ))
        
        booking_id = execute_query("SELECT LAST_INSERT_ID() as id", fetch=True)[0]['id']
        
        # Generate ticket with QR code
        from datetime import datetime, timedelta
        
        # Calculate expiry (journey date + 1 day)
        journey_datetime = datetime.strptime(data['journey_date'], '%Y-%m-%d')
        expiry_datetime = journey_datetime + timedelta(days=1)
        
        execute_query("""
            INSERT INTO ksrtc_tickets (
                booking_id, ticket_number, qr_code_data, expiry_datetime
            ) VALUES (%s, %s, %s, %s)
        """, (booking_id, ticket_number, booking_ref, expiry_datetime))
        
        # Record expense
        execute_query("""
            INSERT INTO ksrtc_user_expenses (
                user_id, booking_id, expense_date, amount, description
            ) VALUES (%s, %s, %s, %s, %s)
        """, (
            current_user['user_id'], booking_id, data['journey_date'],
            data['total_fare'],
            f"KSRTC Bus Ticket: {data['boarding_stop']} to {data['destination_stop']}"
        ))
        
        return jsonify({
            'success': True,
            'message': 'Booking confirmed successfully!',
            'booking': {
                'booking_id': booking_id,
                'booking_reference': booking_ref,
                'ticket_number': ticket_number,
                'passenger_name': data['passenger_name'],
                'boarding_stop': data['boarding_stop'],
                'destination_stop': data['destination_stop'],
                'journey_date': data['journey_date'],
                'seat_numbers': data['seat_numbers'],
                'total_fare': data['total_fare']
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/ksrtc/my-tickets', methods=['GET'])
@token_required
def get_my_ksrtc_tickets(current_user):
    """Get user's KSRTC tickets"""
    try:
        tickets = execute_query("""
            SELECT 
                b.booking_id,
                b.booking_reference,
                b.passenger_name,
                b.boarding_stop,
                b.destination_stop,
                b.journey_date,
                b.seat_numbers,
                b.total_fare,
                b.booking_status,
                b.booked_at,
                t.ticket_number,
                t.is_expired,
                t.expiry_datetime,
                s.departure_time,
                bus.bus_number,
                bus.bus_type,
                r.route_number
            FROM ksrtc_bookings b
            JOIN ksrtc_tickets t ON b.booking_id = t.booking_id
            JOIN ksrtc_schedules s ON b.schedule_id = s.schedule_id
            JOIN ksrtc_buses bus ON s.bus_id = bus.bus_id
            JOIN ksrtc_routes r ON s.route_id = r.route_id
            WHERE b.user_id = %s
            ORDER BY b.journey_date DESC, b.booked_at DESC
        """, (current_user['user_id'],), fetch_all=True)
        
        # Update expired tickets
        from datetime import datetime
        now = datetime.now()
        
        for ticket in tickets:
            if ticket['expiry_datetime'] and ticket['expiry_datetime'] < now:
                if not ticket['is_expired']:
                    execute_query(
                        "UPDATE ksrtc_tickets SET is_expired = TRUE WHERE ticket_number = %s",
                        (ticket['ticket_number'],)
                    )
                ticket['is_expired'] = True
        
        return jsonify({'success': True, 'tickets': tickets})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/ksrtc/expenses', methods=['GET'])
@token_required
def get_ksrtc_expenses(current_user):
    """Get user's KSRTC expenses analytics"""
    try:
        # Daily expenses
        daily = execute_query("""
            SELECT expense_date, SUM(amount) as total_amount, COUNT(*) as booking_count
            FROM ksrtc_user_expenses
            WHERE user_id = %s
            GROUP BY expense_date
            ORDER BY expense_date DESC
            LIMIT 30
        """, (current_user['user_id'],), fetch_all=True)
        
        # Monthly summary
        monthly = execute_query("""
            SELECT 
                DATE_FORMAT(expense_date, '%%Y-%%m') as month,
                SUM(amount) as total_amount,
                COUNT(*) as booking_count
            FROM ksrtc_user_expenses
            WHERE user_id = %s
            GROUP BY month
            ORDER BY month DESC
            LIMIT 12
        """, (current_user['user_id'],), fetch_all=True)
        
        # Total stats
        total_stats = execute_query_one("""
            SELECT 
                SUM(amount) as total_spent,
                COUNT(*) as total_bookings,
                AVG(amount) as avg_per_booking
            FROM ksrtc_user_expenses
            WHERE user_id = %s
        """, (current_user['user_id'],))
        
        return jsonify({
            'success': True,
            'daily_expenses': daily,
            'monthly_expenses': monthly,
            'total_stats': total_stats
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== CANCEL BOOKING ENDPOINTS ====================

@app.route('/api/ksrtc/cancel/<int:booking_id>', methods=['POST'])
@token_required
def cancel_ksrtc_booking(current_user, booking_id):
    """Cancel KSRTC booking"""
    try:
        # Verify booking belongs to user
        booking = execute_query_one("""
            SELECT booking_id, user_id, total_fare, journey_date, booking_status
            FROM ksrtc_bookings WHERE booking_id = %s
        """, (booking_id,))
        
        if not booking:
            return jsonify({'success': False, 'message': 'Booking not found'}), 404
        
        if booking['user_id'] != current_user['user_id']:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        if booking['booking_status'] == 'Cancelled':
            return jsonify({'success': False, 'message': 'Booking already cancelled'}), 400
        
        # Update booking status
        execute_query("""
            UPDATE ksrtc_bookings SET booking_status = 'Cancelled'
            WHERE booking_id = %s
        """, (booking_id,))
        
        # Delete the expense record
        execute_query("""
            DELETE FROM ksrtc_user_expenses WHERE booking_id = %s
        """, (booking_id,))
        
        return jsonify({'success': True, 'message': 'Booking cancelled successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/train/cancel/<int:booking_id>', methods=['POST'])
@token_required
def cancel_train_booking(current_user, booking_id):
    """Cancel train booking"""
    try:
        # Verify booking belongs to user
        booking = execute_query_one("""
            SELECT booking_id, user_id, total_fare, journey_date, booking_status
            FROM train_bookings WHERE booking_id = %s
        """, (booking_id,))
        
        if not booking:
            return jsonify({'success': False, 'message': 'Booking not found'}), 404
        
        if booking['user_id'] != current_user['user_id']:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        if booking['booking_status'] == 'Cancelled':
            return jsonify({'success': False, 'message': 'Booking already cancelled'}), 400
        
        # Update booking status
        execute_query("""
            UPDATE train_bookings SET booking_status = 'Cancelled'
            WHERE booking_id = %s
        """, (booking_id,))
        
        # Delete the expense record
        execute_query("""
            DELETE FROM train_user_expenses WHERE booking_id = %s
        """, (booking_id,))
        
        return jsonify({'success': True, 'message': 'Booking cancelled successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/flight/cancel/<int:booking_id>', methods=['POST'])
@token_required
def cancel_flight_booking(current_user, booking_id):
    """Cancel flight booking"""
    try:
        # Verify booking belongs to user
        booking = execute_query_one("""
            SELECT booking_id, user_id, total_fare, journey_date, booking_status
            FROM flight_bookings WHERE booking_id = %s
        """, (booking_id,))
        
        if not booking:
            return jsonify({'success': False, 'message': 'Booking not found'}), 404
        
        if booking['user_id'] != current_user['user_id']:
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        if booking['booking_status'] == 'Cancelled':
            return jsonify({'success': False, 'message': 'Booking already cancelled'}), 400
        
        # Update booking status
        execute_query("""
            UPDATE flight_bookings SET booking_status = 'Cancelled'
            WHERE booking_id = %s
        """, (booking_id,))
        
        # Delete the expense record
        execute_query("""
            DELETE FROM flight_user_expenses WHERE booking_id = %s
        """, (booking_id,))
        
        return jsonify({'success': True, 'message': 'Booking cancelled successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== TRAIN BOOKING APIs ====================

@app.route('/api/trains/stations', methods=['GET'])
def get_train_stations():
    """Get all train stations"""
    try:
        stations = execute_query("""
            SELECT station_code, station_name, city
            FROM train_stations
            ORDER BY station_name
        """, fetch=True)
        
        if not stations:
            return jsonify({'success': True, 'stations': []})
        
        return jsonify({
            'success': True,
            'stations': [
                {
                    'code': s['station_code'],
                    'name': s['station_name'],
                    'city': s['city']
                }
                for s in stations
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/trains/search', methods=['GET'])
def search_trains():
    """Search trains by route and date"""
    try:
        from_station = request.args.get('from')
        to_station = request.args.get('to')
        journey_date = request.args.get('date')
        coach_class = request.args.get('class', 'SLEEPER')
        
        if not all([from_station, to_station, journey_date]):
            return jsonify({'success': False, 'message': 'Missing required parameters'}), 400
        
        # Get day of week
        date_obj = datetime.datetime.strptime(journey_date, '%Y-%m-%d')
        day_name = date_obj.strftime('%A').lower()
        
        # Find trains with both stations in route
        trains = execute_query("""
            SELECT DISTINCT
                t.train_id,
                t.train_number,
                t.train_name,
                t.train_type,
                s1.arrival_time as from_arrival,
                s1.departure_time as from_departure,
                s1.stop_number as from_stop,
                s2.arrival_time as to_arrival,
                s2.departure_time as to_departure,
                s2.stop_number as to_stop,
                s2.distance_km - s1.distance_km as distance,
                rd.{} as runs_on_day
            FROM trains t
            JOIN train_schedules s1 ON t.train_id = s1.train_id AND s1.station_code = %s
            JOIN train_schedules s2 ON t.train_id = s2.train_id AND s2.station_code = %s
            JOIN train_running_days rd ON t.train_id = rd.train_id
            WHERE s1.stop_number < s2.stop_number
            AND rd.{} = 1
            AND t.is_active = 1
            ORDER BY s1.departure_time
        """.format(day_name, day_name), (from_station, to_station), fetch=True)
        
        if not trains:
            return jsonify({'success': True, 'trains': [], 'count': 0})
        
        result = []
        for train in trains:
            # Calculate fare based on distance and class
            distance = float(train['distance']) if train.get('distance') else 100
            base_fare = distance * 0.5  # 50 paisa per km base
            
            class_multiplier = {
                'AC-1': 5.0,
                'AC-2': 3.5,
                'AC-3': 2.5,
                'SLEEPER': 1.5,
                'GENERAL': 1.0
            }
            
            fare = base_fare * class_multiplier.get(coach_class, 1.5)
            
            result.append({
                'train_id': train['train_id'],
                'train_number': train['train_number'],
                'train_name': train['train_name'],
                'train_type': train['train_type'],
                'from_departure': str(train['from_departure']) if train.get('from_departure') else 'N/A',
                'to_arrival': str(train['to_arrival']) if train.get('to_arrival') else 'N/A',
                'distance_km': round(distance, 2),
                'fare': round(fare, 2)
            })
        
        return jsonify({
            'success': True,
            'trains': result,
            'count': len(result)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/trains/coaches', methods=['GET'])
def get_train_coaches():
    """Get coaches and berths for a train"""
    try:
        train_id = request.args.get('train_id')
        coach_type = request.args.get('coach_type', 'SLEEPER')
        
        if not train_id:
            return jsonify({'success': False, 'message': 'train_id required'}), 400
        
        # Get coaches
        coaches = execute_query("""
            SELECT coach_id, coach_number, coach_type, total_berths
            FROM train_coaches
            WHERE train_id = %s AND coach_type = %s
            ORDER BY coach_number
        """, (train_id, coach_type), fetch=True)
        
        if not coaches:
            return jsonify({'success': True, 'coaches': []})
        
        result = []
        for coach in coaches:
            # Get berths for this coach
            berths = execute_query("""
                SELECT berth_id, berth_number, berth_type, is_available
                FROM train_berths
                WHERE coach_id = %s
                ORDER BY CAST(berth_number AS UNSIGNED)
            """, (coach['coach_id'],), fetch=True)
            
            result.append({
                'coach_id': coach['coach_id'],
                'coach_number': coach['coach_number'],
                'coach_type': coach['coach_type'],
                'total_berths': coach['total_berths'],
                'berths': [
                    {
                        'berth_id': b['berth_id'],
                        'berth_number': b['berth_number'],
                        'berth_type': b['berth_type'],
                        'is_available': bool(b['is_available'])
                    }
                    for b in (berths or [])
                ]
            })
        
        return jsonify({
            'success': True,
            'coaches': result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/trains/book', methods=['POST'])
@token_required
def book_train_ticket(current_user):
    """Book train ticket"""
    try:
        data = request.json
        
        # Generate PNR
        import random
        pnr = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        
        # Calculate total fare
        base_fare = float(data.get('base_fare', 500))
        reservation_charges = 40.00
        total_fare = base_fare + reservation_charges
        
        # Insert booking
        execute_query("""
            INSERT INTO train_bookings 
            (user_id, train_id, pnr_number, passenger_name, passenger_age, 
             passenger_gender, passenger_phone, passenger_email, from_station, 
             to_station, journey_date, coach_type, berth_numbers, base_fare, 
             reservation_charges, total_fare, booking_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Confirmed')
        """, (
            current_user['user_id'],
            data['train_id'],
            pnr,
            data['passenger_name'],
            data['passenger_age'],
            data['passenger_gender'],
            data['passenger_phone'],
            data.get('passenger_email', ''),
            data['from_station'],
            data['to_station'],
            data['journey_date'],
            data['coach_type'],
            ','.join(data['berth_numbers']),
            base_fare,
            reservation_charges,
            total_fare
        ))
        
        # Get booking ID
        booking_result = execute_query("SELECT LAST_INSERT_ID() as id", fetch=True)
        if not booking_result:
            return jsonify({'success': False, 'message': 'Failed to create booking'}), 500
        booking_id = booking_result[0]['id']
        
        # Mark berths as unavailable
        for berth_id in data.get('berth_ids', []):
            execute_query("UPDATE train_berths SET is_available = FALSE WHERE berth_id = %s", (berth_id,))
        
        # Create ticket
        ticket_number = f"TKT{booking_id:08d}"
        qr_data = f"PNR:{pnr}|TRAIN:{data.get('train_number')}|PASSENGER:{data['passenger_name']}"
        
        # Calculate expiry (journey date + 1 day)
        journey_dt = datetime.datetime.strptime(data['journey_date'], '%Y-%m-%d')
        expiry_dt = journey_dt + datetime.timedelta(days=1)
        
        execute_query("""
            INSERT INTO train_tickets 
            (booking_id, ticket_number, qr_code_data, expiry_datetime)
            VALUES (%s, %s, %s, %s)
        """, (booking_id, ticket_number, qr_data, expiry_dt))
        
        # Add expense
        execute_query("""
            INSERT INTO train_user_expenses 
            (user_id, booking_id, expense_date, amount, category, description)
            VALUES (%s, %s, %s, %s, 'Train Ticket', %s)
        """, (
            current_user['user_id'],
            booking_id,
            data['journey_date'],
            total_fare,
            f"Train {data.get('train_number', 'N/A')} - {data['from_station']} to {data['to_station']}"
        ))
        
        return jsonify({
            'success': True,
            'message': 'Ticket booked successfully!',
            'booking_id': booking_id,
            'pnr': pnr,
            'ticket_number': ticket_number,
            'total_fare': total_fare
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/trains/my-tickets', methods=['GET'])
@token_required
def get_train_tickets(current_user):
    """Get user's train tickets"""
    try:
        tickets = execute_query("""
            SELECT 
                b.booking_id,
                b.pnr_number,
                b.passenger_name,
                b.journey_date,
                b.from_station,
                b.to_station,
                b.coach_type,
                b.berth_numbers,
                b.total_fare,
                b.booking_status,
                t.train_number,
                t.train_name,
                tk.ticket_number,
                tk.qr_code_data,
                tk.is_expired,
                b.booked_at
            FROM train_bookings b
            JOIN trains t ON b.train_id = t.train_id
            LEFT JOIN train_tickets tk ON b.booking_id = tk.booking_id
            WHERE b.user_id = %s
            ORDER BY b.booked_at DESC
        """, (current_user['user_id'],), fetch=True)
        
        if not tickets:
            return jsonify({'success': True, 'tickets': [], 'count': 0})
        
        result = []
        for ticket in tickets:
            result.append({
                'booking_id': ticket['booking_id'],
                'pnr': ticket['pnr_number'],
                'passenger_name': ticket['passenger_name'],
                'journey_date': str(ticket['journey_date']),
                'from_station': ticket['from_station'],
                'to_station': ticket['to_station'],
                'coach_type': ticket['coach_type'],
                'berths': ticket['berth_numbers'],
                'total_fare': float(ticket['total_fare']),
                'status': ticket['booking_status'],
                'train_number': ticket['train_number'],
                'train_name': ticket['train_name'],
                'ticket_number': ticket['ticket_number'],
                'qr_code': ticket['qr_code_data'],
                'is_expired': bool(ticket['is_expired']) if ticket.get('is_expired') else False,
                'booked_at': str(ticket['booked_at'])
            })
        
        return jsonify({
            'success': True,
            'tickets': result,
            'count': len(result)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== FLIGHT BOOKING APIs ====================

@app.route('/api/flights/airports', methods=['GET'])
def get_airports():
    """Get all airports"""
    try:
        airports = execute_query("""
            SELECT airport_code, airport_name, city
            FROM airports
            ORDER BY city
        """, fetch=True)
        
        if not airports:
            return jsonify({'success': True, 'airports': []})
        
        return jsonify({
            'success': True,
            'airports': [
                {
                    'code': a['airport_code'],
                    'name': a['airport_name'],
                    'city': a['city']
                }
                for a in airports
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/flights/search', methods=['GET'])
def search_flights():
    """Search flights by route and date"""
    try:
        from_airport = request.args.get('from')
        to_airport = request.args.get('to')
        journey_date = request.args.get('date')
        seat_class = request.args.get('class', 'Economy')
        
        if not all([from_airport, to_airport, journey_date]):
            return jsonify({'success': False, 'message': 'Missing required parameters'}), 400
        
        # Get day of week
        date_obj = datetime.datetime.strptime(journey_date, '%Y-%m-%d')
        day_name = date_obj.strftime('%A').lower()
        
        # Find flights
        flights = execute_query("""
            SELECT 
                f.flight_id,
                f.flight_number,
                f.departure_time,
                f.arrival_time,
                f.economy_seats,
                f.business_seats,
                f.flight_duration_mins,
                a.airline_name,
                ap1.city as from_city,
                ap2.city as to_city,
                fs.{} as runs_on_day
            FROM flights f
            JOIN airlines a ON f.airline_id = a.airline_id
            JOIN airports ap1 ON f.origin_code = ap1.airport_code
            JOIN airports ap2 ON f.destination_code = ap2.airport_code
            JOIN flight_schedules fs ON f.flight_id = fs.flight_id
            WHERE f.origin_code = %s
            AND f.destination_code = %s
            AND fs.{} = TRUE
            AND f.is_active = TRUE
            ORDER BY f.departure_time
        """.format(day_name, day_name), (from_airport, to_airport), fetch=True)
        
        if not flights:
            return jsonify({'success': True, 'flights': [], 'count': 0})
        
        result = []
        for flight in flights:
            # Calculate fare based on duration
            duration = flight.get('flight_duration_mins', 120)
            base_fare = 3000 if seat_class == 'Economy' else 8000
            if duration > 120:
                base_fare = 5000 if seat_class == 'Economy' else 12000
            taxes = 500
            total_fare = base_fare + taxes
            
            result.append({
                'flight_id': flight['flight_id'],
                'flight_number': flight['flight_number'],
                'airline': flight['airline_name'],
                'departure_time': str(flight['departure_time']) if flight.get('departure_time') else 'N/A',
                'arrival_time': str(flight['arrival_time']) if flight.get('arrival_time') else 'N/A',
                'duration_mins': duration,
                'from_city': flight['from_city'],
                'to_city': flight['to_city'],
                'base_fare': base_fare,
                'taxes': taxes,
                'total_fare': total_fare,
                'available_seats': flight['economy_seats'] if seat_class == 'Economy' else flight['business_seats']
            })
        
        return jsonify({
            'success': True,
            'flights': result,
            'count': len(result)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/flights/seats', methods=['GET'])
def get_flight_seats():
    """Get seat map for a flight"""
    try:
        flight_id = request.args.get('flight_id')
        seat_class = request.args.get('class', 'Economy')
        
        if not flight_id:
            return jsonify({'success': False, 'message': 'flight_id required'}), 400
        
        # Get seats
        seats = execute_query("""
            SELECT 
                seat_id,
                seat_number,
                seat_class,
                seat_row,
                seat_column,
                is_window,
                is_aisle,
                is_available
            FROM flight_seats
            WHERE flight_id = %s AND seat_class = %s
            ORDER BY seat_row, seat_column
        """, (flight_id, seat_class), fetch=True)
        
        if not seats:
            return jsonify({'success': True, 'seats': []})
        
        result = []
        for seat in seats:
            result.append({
                'seat_id': seat['seat_id'],
                'seat_number': seat['seat_number'],
                'seat_class': seat['seat_class'],
                'row': seat['seat_row'],
                'column': seat['seat_column'],
                'is_window': bool(seat['is_window']),
                'is_aisle': bool(seat['is_aisle']),
                'is_available': bool(seat['is_available'])
            })
        
        return jsonify({
            'success': True,
            'seats': result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/flights/book', methods=['POST'])
@token_required
def book_flight(current_user):
    """Book flight ticket"""
    try:
        data = request.json
        
        # Generate booking reference
        import random
        import string
        booking_ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Calculate total fare
        base_fare = float(data.get('base_fare', 3000))
        taxes = float(data.get('taxes', 500))
        total_fare = base_fare + taxes
        
        # Insert booking
        booking_id = execute_query("""
            INSERT INTO flight_bookings 
            (user_id, flight_id, booking_reference, passenger_name, passenger_age, 
             passenger_gender, passenger_phone, passenger_email, from_airport, 
             to_airport, journey_date, seat_class, seat_numbers, base_fare, 
             taxes_fees, total_fare, booking_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Confirmed')
        """, (
            current_user['user_id'],
            data['flight_id'],
            booking_ref,
            data['passenger_name'],
            data['passenger_age'],
            data['passenger_gender'],
            data['passenger_phone'],
            data['passenger_email'],
            data['from_airport'],
            data['to_airport'],
            data['journey_date'],
            data['seat_class'],
            data['seat_number'],
            base_fare,
            taxes,
            total_fare
        ))
        
        # Mark seat as unavailable
        if 'seat_id' in data:
            execute_query("UPDATE flight_seats SET is_available = FALSE WHERE seat_id = %s", (data['seat_id'],))
        
        # Create boarding pass
        pass_number = f"BP{booking_id:08d}"
        barcode_data = f"REF:{booking_ref}|FLIGHT:{data.get('flight_number')}|PASSENGER:{data['passenger_name']}|SEAT:{data['seat_number']}"
        
        execute_query("""
            INSERT INTO boarding_passes 
            (booking_id, boarding_pass_number, barcode_data)
            VALUES (%s, %s, %s)
        """, (booking_id, pass_number, barcode_data))
        
        # Add expense
        execute_query("""
            INSERT INTO flight_user_expenses 
            (user_id, booking_id, expense_date, amount, category, description)
            VALUES (%s, %s, %s, %s, 'Flight Ticket', %s)
        """, (
            current_user['user_id'],
            booking_id,
            data['journey_date'],
            total_fare,
            f"Flight {data.get('flight_number', 'N/A')} - {data['from_airport']} to {data['to_airport']}"
        ))
        
        return jsonify({
            'success': True,
            'message': 'Flight booked successfully!',
            'booking_id': booking_id,
            'booking_reference': booking_ref,
            'boarding_pass': pass_number,
            'total_fare': total_fare
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/flights/my-tickets', methods=['GET'])
@token_required
def get_flight_tickets(current_user):
    """Get user's flight tickets"""
    try:
        tickets = execute_query("""
            SELECT 
                b.booking_id,
                b.booking_reference,
                b.passenger_name,
                b.journey_date,
                b.from_airport,
                b.to_airport,
                b.seat_class,
                b.seat_numbers,
                b.total_fare,
                b.booking_status,
                f.flight_number,
                a.airline_name,
                bp.boarding_pass_number,
                bp.barcode_data,
                b.booked_at
            FROM flight_bookings b
            JOIN flights f ON b.flight_id = f.flight_id
            JOIN airlines a ON f.airline_id = a.airline_id
            LEFT JOIN boarding_passes bp ON b.booking_id = bp.booking_id
            WHERE b.user_id = %s
            ORDER BY b.booked_at DESC
        """, (current_user['user_id'],))
        
        result = []
        for ticket in tickets:
            result.append({
                'booking_id': ticket[0],
                'booking_reference': ticket[1],
                'passenger_name': ticket[2],
                'journey_date': str(ticket[3]),
                'from_airport': ticket[4],
                'to_airport': ticket[5],
                'seat_class': ticket[6],
                'seat': ticket[7],
                'total_fare': float(ticket[8]),
                'status': ticket[9],
                'flight_number': ticket[10],
                'airline': ticket[11],
                'boarding_pass': ticket[12],
                'barcode': ticket[13],
                'booked_at': str(ticket[14])
            })
        
        return jsonify({
            'success': True,
            'tickets': result,
            'count': len(result)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== UNIFIED TICKETS & EXPENSES ====================

@app.route('/api/tickets/all', methods=['GET'])
@token_required
def get_all_tickets(current_user):
    """Get all user tickets (KSRTC, Trains, Flights) with unified format"""
    try:
        all_tickets = []
        
        # Get KSRTC tickets
        ksrtc_tickets = execute_query("""
            SELECT 
                b.booking_id,
                b.booking_reference,
                b.passenger_name,
                b.boarding_stop,
                b.destination_stop,
                b.journey_date,
                b.seat_numbers,
                b.total_fare,
                b.booking_status,
                b.booked_at,
                t.ticket_number,
                t.is_expired,
                t.expiry_datetime,
                s.departure_time,
                bus.bus_number,
                bus.bus_type
            FROM ksrtc_bookings b
            LEFT JOIN ksrtc_tickets t ON b.booking_id = t.booking_id
            LEFT JOIN ksrtc_schedules s ON b.schedule_id = s.schedule_id
            LEFT JOIN ksrtc_buses bus ON s.bus_id = bus.bus_id
            WHERE b.user_id = %s
            ORDER BY b.journey_date DESC, b.booked_at DESC
        """, (current_user['user_id'],), fetch=True) or []
        
        for ticket in ksrtc_tickets:
            all_tickets.append({
                'type': 'KSRTC',
                'booking_id': ticket['booking_id'],
                'ticket_number': ticket.get('ticket_number', 'N/A'),
                'booking_reference': ticket['booking_reference'],
                'passenger_name': ticket['passenger_name'],
                'from': ticket['boarding_stop'],
                'to': ticket['destination_stop'],
                'journey_date': str(ticket['journey_date']),
                'departure_time': str(ticket['departure_time']) if ticket.get('departure_time') else 'N/A',
                'seat_numbers': ticket['seat_numbers'],
                'bus_number': ticket.get('bus_number', 'N/A'),
                'bus_type': ticket.get('bus_type', 'N/A'),
                'total_fare': float(ticket['total_fare']),
                'booking_status': ticket['booking_status'],
                'is_expired': bool(ticket.get('is_expired', False)),
                'expiry_datetime': str(ticket['expiry_datetime']) if ticket.get('expiry_datetime') else None,
                'booked_at': str(ticket['booked_at'])
            })
        
        # Get Train tickets
        train_tickets = execute_query("""
            SELECT 
                b.booking_id,
                b.pnr_number,
                b.passenger_name,
                b.journey_date,
                b.from_station,
                b.to_station,
                b.coach_type,
                b.berth_numbers,
                b.total_fare,
                b.booking_status,
                t.train_number,
                t.train_name,
                tk.ticket_number,
                tk.qr_code_data,
                tk.is_expired,
                tk.expiry_datetime,
                b.booked_at
            FROM train_bookings b
            JOIN trains t ON b.train_id = t.train_id
            LEFT JOIN train_tickets tk ON b.booking_id = tk.booking_id
            WHERE b.user_id = %s
            ORDER BY b.journey_date DESC, b.booked_at DESC
        """, (current_user['user_id'],), fetch=True) or []
        
        for ticket in train_tickets:
            all_tickets.append({
                'type': 'TRAIN',
                'booking_id': ticket['booking_id'],
                'ticket_number': ticket.get('ticket_number', 'N/A'),
                'pnr': ticket['pnr_number'],
                'passenger_name': ticket['passenger_name'],
                'from': ticket['from_station'],
                'to': ticket['to_station'],
                'journey_date': str(ticket['journey_date']),
                'train_number': ticket['train_number'],
                'train_name': ticket['train_name'],
                'coach_type': ticket['coach_type'],
                'berth_numbers': ticket['berth_numbers'],
                'total_fare': float(ticket['total_fare']),
                'booking_status': ticket['booking_status'],
                'is_expired': bool(ticket.get('is_expired', False)),
                'expiry_datetime': str(ticket['expiry_datetime']) if ticket.get('expiry_datetime') else None,
                'qr_code': ticket.get('qr_code_data'),
                'booked_at': str(ticket['booked_at'])
            })
        
        # Get Flight tickets
        flight_tickets = execute_query("""
            SELECT 
                b.booking_id,
                b.booking_reference,
                b.passenger_name,
                b.journey_date,
                b.from_airport,
                b.to_airport,
                b.seat_class,
                b.seat_numbers,
                b.total_fare,
                b.booking_status,
                f.flight_number,
                a.airline_name,
                b.booked_at
            FROM flight_bookings b
            JOIN flights f ON b.flight_id = f.flight_id
            JOIN airlines a ON f.airline_id = a.airline_id
            WHERE b.user_id = %s
            ORDER BY b.journey_date DESC, b.booked_at DESC
        """, (current_user['user_id'],), fetch=True) or []
        
        for ticket in flight_tickets:
            # Check if flight has expired (journey date is in the past)
            journey_date = ticket['journey_date']
            is_expired = journey_date < datetime.datetime.now().date()
            
            all_tickets.append({
                'type': 'FLIGHT',
                'booking_id': ticket['booking_id'],
                'ticket_number': ticket['booking_reference'],
                'pnr': ticket['booking_reference'],
                'passenger_name': ticket['passenger_name'],
                'from': ticket['from_airport'],
                'to': ticket['to_airport'],
                'journey_date': str(ticket['journey_date']),
                'flight_number': ticket['flight_number'],
                'airline_name': ticket['airline_name'],
                'travel_class': ticket['seat_class'],
                'seat_numbers': ticket['seat_numbers'],
                'total_fare': float(ticket['total_fare']),
                'booking_status': ticket['booking_status'],
                'is_expired': is_expired,
                'expiry_datetime': None,
                'booked_at': str(ticket['booked_at'])
            })
        
        # Sort all tickets by journey date
        all_tickets.sort(key=lambda x: x['journey_date'], reverse=True)
        
        # Count by status
        active = len([t for t in all_tickets if not t['is_expired'] and t['booking_status'] == 'Confirmed'])
        expired = len([t for t in all_tickets if t['is_expired']])
        cancelled = len([t for t in all_tickets if t['booking_status'] == 'Cancelled'])
        
        return jsonify({
            'success': True,
            'tickets': all_tickets,
            'count': {
                'total': len(all_tickets),
                'active': active,
                'expired': expired,
                'cancelled': cancelled
            }
        })
        
    except Exception as e:
        print(f"✗ Error in get_all_tickets: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/expenses/all', methods=['GET'])
@token_required
def get_all_expenses(current_user):
    """Get all user expenses across all transport types"""
    try:
        all_expenses = []
        
        # KSRTC expenses
        ksrtc_exp = execute_query("""
            SELECT 
                expense_id,
                booking_id,
                expense_date,
                amount,
                description,
                'KSRTC' as category
            FROM ksrtc_user_expenses
            WHERE user_id = %s
        """, (current_user['user_id'],), fetch=True) or []
        all_expenses.extend(ksrtc_exp)
        
        # Train expenses
        train_exp = execute_query("""
            SELECT 
                expense_id,
                booking_id,
                expense_date,
                amount,
                description,
                category
            FROM train_user_expenses
            WHERE user_id = %s
        """, (current_user['user_id'],), fetch=True) or []
        all_expenses.extend(train_exp)
        
        # Flight expenses
        flight_exp = execute_query("""
            SELECT 
                expense_id,
                booking_id,
                expense_date,
                amount,
                description,
                'FLIGHT' as category
            FROM flight_user_expenses
            WHERE user_id = %s
        """, (current_user['user_id'],), fetch=True) or []
        all_expenses.extend(flight_exp)
        
        # Sort by date
        all_expenses.sort(key=lambda x: x['expense_date'], reverse=True)
        
        # Calculate totals
        total_spent = sum(float(exp['amount']) for exp in all_expenses)
        
        # Get booking statistics
        ksrtc_stats = execute_query("""
            SELECT 
                COUNT(*) as total_bookings,
                SUM(CASE WHEN booking_status = 'Confirmed' THEN 1 ELSE 0 END) as confirmed,
                SUM(CASE WHEN booking_status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled
            FROM ksrtc_bookings WHERE user_id = %s
        """, (current_user['user_id'],), fetch=True)[0] if execute_query("""
            SELECT COUNT(*) as cnt FROM ksrtc_bookings WHERE user_id = %s
        """, (current_user['user_id'],), fetch=True) else {'total_bookings': 0, 'confirmed': 0, 'cancelled': 0}
        
        train_stats = execute_query("""
            SELECT 
                COUNT(*) as total_bookings,
                SUM(CASE WHEN booking_status = 'Confirmed' THEN 1 ELSE 0 END) as confirmed,
                SUM(CASE WHEN booking_status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled
            FROM train_bookings WHERE user_id = %s
        """, (current_user['user_id'],), fetch=True)[0] if execute_query("""
            SELECT COUNT(*) as cnt FROM train_bookings WHERE user_id = %s
        """, (current_user['user_id'],), fetch=True) else {'total_bookings': 0, 'confirmed': 0, 'cancelled': 0}
        
        flight_stats = execute_query("""
            SELECT 
                COUNT(*) as total_bookings,
                SUM(CASE WHEN booking_status = 'Confirmed' THEN 1 ELSE 0 END) as confirmed,
                SUM(CASE WHEN booking_status = 'Cancelled' THEN 1 ELSE 0 END) as cancelled
            FROM flight_bookings WHERE user_id = %s
        """, (current_user['user_id'],), fetch=True)[0] if execute_query("""
            SELECT COUNT(*) as cnt FROM flight_bookings WHERE user_id = %s
        """, (current_user['user_id'],), fetch=True) else {'total_bookings': 0, 'confirmed': 0, 'cancelled': 0}
        
        # Monthly summary
        from collections import defaultdict
        monthly = defaultdict(lambda: {'total': 0, 'count': 0, 'ksrtc': 0, 'train': 0, 'flight': 0})
        daily = defaultdict(lambda: {'total': 0, 'count': 0, 'ksrtc': 0, 'train': 0, 'flight': 0})
        
        for exp in all_expenses:
            month_key = str(exp['expense_date'])[:7]  # YYYY-MM
            day_key = str(exp['expense_date'])  # YYYY-MM-DD
            
            monthly[month_key]['total'] += float(exp['amount'])
            monthly[month_key]['count'] += 1
            daily[day_key]['total'] += float(exp['amount'])
            daily[day_key]['count'] += 1
            
            # Track mode counts
            if exp['category'] == 'KSRTC':
                monthly[month_key]['ksrtc'] += 1
                daily[day_key]['ksrtc'] += 1
            elif exp['category'] == 'Train Ticket':
                monthly[month_key]['train'] += 1
                daily[day_key]['train'] += 1
            elif exp['category'] == 'FLIGHT':
                monthly[month_key]['flight'] += 1
                daily[day_key]['flight'] += 1
        
        monthly_summary = [
            {
                'month': month,
                'total_amount': data['total'],
                'booking_count': data['count'],
                'most_used_mode': 'KSRTC' if data['ksrtc'] >= max(data['train'], data['flight']) else ('Train' if data['train'] >= data['flight'] else 'Flight'),
                'ksrtc_count': data['ksrtc'],
                'train_count': data['train'],
                'flight_count': data['flight']
            }
            for month, data in sorted(monthly.items(), reverse=True)
        ]
        
        daily_summary = [
            {
                'date': day,
                'total_amount': data['total'],
                'booking_count': data['count'],
                'most_used_mode': 'KSRTC' if data['ksrtc'] >= max(data['train'], data['flight']) else ('Train' if data['train'] >= data['flight'] else 'Flight'),
                'ksrtc_count': data['ksrtc'],
                'train_count': data['train'],
                'flight_count': data['flight']
            }
            for day, data in sorted(daily.items(), reverse=True)
        ]
        
        return jsonify({
            'success': True,
            'expenses': [
                {
                    'expense_id': exp['expense_id'],
                    'booking_id': exp['booking_id'],
                    'date': str(exp['expense_date']),
                    'amount': float(exp['amount']),
                    'description': exp['description'],
                    'category': exp['category']
                }
                for exp in all_expenses
            ],
            'summary': {
                'total_spent': total_spent,
                'total_bookings': len(all_expenses),
                'avg_per_booking': total_spent / len(all_expenses) if all_expenses else 0,
                'monthly': monthly_summary[:12],  # Last 12 months
                'daily': daily_summary[:30]  # Last 30 days
            },
            'booking_stats': {
                'ksrtc': {
                    'total': int(ksrtc_stats.get('total_bookings', 0) or 0),
                    'confirmed': int(ksrtc_stats.get('confirmed', 0) or 0),
                    'cancelled': int(ksrtc_stats.get('cancelled', 0) or 0)
                },
                'train': {
                    'total': int(train_stats.get('total_bookings', 0) or 0),
                    'confirmed': int(train_stats.get('confirmed', 0) or 0),
                    'cancelled': int(train_stats.get('cancelled', 0) or 0)
                },
                'flight': {
                    'total': int(flight_stats.get('total_bookings', 0) or 0),
                    'confirmed': int(flight_stats.get('confirmed', 0) or 0),
                    'cancelled': int(flight_stats.get('cancelled', 0) or 0)
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== PAGE ROUTES ====================

@app.route('/trains')
def trains_page():
    """Serve trains booking page"""
    return send_from_directory(app.static_folder, 'trains.html')


@app.route('/flights')
def flights_page():
    """Serve flights booking page"""
    return send_from_directory(app.static_folder, 'flights.html')


# ==================== ADMIN SEAT STATISTICS ====================

@app.route('/api/admin/seat-stats/ksrtc', methods=['GET'])
@token_required
def get_ksrtc_seat_stats(current_user):
    """Get KSRTC seat statistics"""
    try:
        stats = execute_query_one("""
            SELECT 
                COUNT(*) as total_seats,
                SUM(CASE WHEN is_available = TRUE THEN 1 ELSE 0 END) as available_seats,
                SUM(CASE WHEN is_available = FALSE THEN 1 ELSE 0 END) as booked_seats
            FROM ksrtc_seats
        """)
        
        total = stats['total_seats'] or 0
        available = stats['available_seats'] or 0
        booked = stats['booked_seats'] or 0
        
        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'available': available,
                'booked': booked,
                'available_percent': round((available / total * 100), 1) if total > 0 else 0,
                'booked_percent': round((booked / total * 100), 1) if total > 0 else 0
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/seat-stats/train', methods=['GET'])
@token_required
def get_train_seat_stats(current_user):
    """Get train berth statistics"""
    try:
        stats = execute_query_one("""
            SELECT 
                COUNT(*) as total_berths,
                SUM(CASE WHEN is_available = TRUE THEN 1 ELSE 0 END) as available_berths,
                SUM(CASE WHEN is_available = FALSE THEN 1 ELSE 0 END) as booked_berths
            FROM train_berths
        """)
        
        total = stats['total_berths'] or 0
        available = stats['available_berths'] or 0
        booked = stats['booked_berths'] or 0
        
        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'available': available,
                'booked': booked,
                'available_percent': round((available / total * 100), 1) if total > 0 else 0,
                'booked_percent': round((booked / total * 100), 1) if total > 0 else 0
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/seat-stats/flight', methods=['GET'])
@token_required
def get_flight_seat_stats(current_user):
    """Get flight seat statistics"""
    try:
        stats = execute_query_one("""
            SELECT 
                COUNT(*) as total_seats,
                SUM(CASE WHEN is_available = TRUE THEN 1 ELSE 0 END) as available_seats,
                SUM(CASE WHEN is_available = FALSE THEN 1 ELSE 0 END) as booked_seats
            FROM flight_seats
        """)
        
        total = stats['total_seats'] or 0
        available = stats['available_seats'] or 0
        booked = stats['booked_seats'] or 0
        
        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'available': available,
                'booked': booked,
                'available_percent': round((available / total * 100), 1) if total > 0 else 0,
                'booked_percent': round((booked / total * 100), 1) if total > 0 else 0
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/revenue/daily', methods=['GET'])
@token_required
def get_daily_revenue(current_user):
    """Get comprehensive daily revenue breakdown for admin"""
    try:
        # Get date parameter (default to today)
        from datetime import datetime, timedelta
        date_param = request.args.get('date')
        
        if date_param:
            target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
        else:
            target_date = datetime.now().date()
        
        is_admin = current_user.get('user_type') == 'admin'
        
        if is_admin:
            # KSRTC revenue for the day
            ksrtc_revenue = execute_query("""
                SELECT 
                    COUNT(*) as total_bookings,
                    COUNT(CASE WHEN booking_status = 'Confirmed' THEN 1 END) as confirmed_bookings,
                    COUNT(CASE WHEN booking_status = 'Cancelled' THEN 1 END) as cancelled_bookings,
                    COALESCE(SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END), 0) as total_revenue,
                    COALESCE(AVG(CASE WHEN booking_status = 'Confirmed' THEN total_fare END), 0) as avg_fare
                FROM ksrtc_bookings
                WHERE DATE(journey_date) = %s
            """, (target_date,), fetch=True)
            
            # Train revenue for the day
            train_revenue = execute_query("""
                SELECT 
                    COUNT(*) as total_bookings,
                    COUNT(CASE WHEN booking_status = 'Confirmed' THEN 1 END) as confirmed_bookings,
                    COUNT(CASE WHEN booking_status = 'Cancelled' THEN 1 END) as cancelled_bookings,
                    COALESCE(SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END), 0) as total_revenue,
                    COALESCE(AVG(CASE WHEN booking_status = 'Confirmed' THEN total_fare END), 0) as avg_fare
                FROM train_bookings
                WHERE DATE(journey_date) = %s
            """, (target_date,), fetch=True)
            
            # Flight revenue for the day
            flight_revenue = execute_query("""
                SELECT 
                    COUNT(*) as total_bookings,
                    COUNT(CASE WHEN booking_status = 'Confirmed' THEN 1 END) as confirmed_bookings,
                    COUNT(CASE WHEN booking_status = 'Cancelled' THEN 1 END) as cancelled_bookings,
                    COALESCE(SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END), 0) as total_revenue,
                    COALESCE(AVG(CASE WHEN booking_status = 'Confirmed' THEN total_fare END), 0) as avg_fare
                FROM flight_bookings
                WHERE DATE(journey_date) = %s
            """, (target_date,), fetch=True)
            
            # Top users by spending for the day
            top_users = execute_query("""
                SELECT 
                    u.user_id,
                    u.username,
                    u.email,
                    SUM(total_revenue) as total_spent,
                    SUM(booking_count) as total_bookings
                FROM (
                    SELECT user_id, SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END) as total_revenue, COUNT(*) as booking_count
                    FROM ksrtc_bookings WHERE DATE(journey_date) = %s GROUP BY user_id
                    UNION ALL
                    SELECT user_id, SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END) as total_revenue, COUNT(*) as booking_count
                    FROM train_bookings WHERE DATE(journey_date) = %s GROUP BY user_id
                    UNION ALL
                    SELECT user_id, SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END) as total_revenue, COUNT(*) as booking_count
                    FROM flight_bookings WHERE DATE(journey_date) = %s GROUP BY user_id
                ) as combined
                JOIN users u ON combined.user_id = u.user_id
                GROUP BY u.user_id, u.username, u.email
                HAVING SUM(total_revenue) > 0
                ORDER BY total_spent DESC
                LIMIT 10
            """, (target_date, target_date, target_date), fetch=True) or []
            
            # Hourly revenue trend
            hourly_trend = execute_query("""
                SELECT 
                    HOUR(booking_time) as hour,
                    COUNT(*) as bookings,
                    SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END) as revenue,
                    'KSRTC' as type
                FROM ksrtc_bookings
                WHERE DATE(booking_time) = %s
                GROUP BY HOUR(booking_time)
                UNION ALL
                SELECT 
                    HOUR(booking_time) as hour,
                    COUNT(*) as bookings,
                    SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END) as revenue,
                    'Train' as type
                FROM train_bookings
                WHERE DATE(booking_time) = %s
                GROUP BY HOUR(booking_time)
                UNION ALL
                SELECT 
                    HOUR(booking_time) as hour,
                    COUNT(*) as bookings,
                    SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END) as revenue,
                    'Flight' as type
                FROM flight_bookings
                WHERE DATE(booking_time) = %s
                GROUP BY HOUR(booking_time)
                ORDER BY hour, type
            """, (target_date, target_date, target_date), fetch=True) or []
            
            ksrtc = ksrtc_revenue[0] if ksrtc_revenue else {'total_bookings': 0, 'confirmed_bookings': 0, 'cancelled_bookings': 0, 'total_revenue': 0, 'avg_fare': 0}
            train = train_revenue[0] if train_revenue else {'total_bookings': 0, 'confirmed_bookings': 0, 'cancelled_bookings': 0, 'total_revenue': 0, 'avg_fare': 0}
            flight = flight_revenue[0] if flight_revenue else {'total_bookings': 0, 'confirmed_bookings': 0, 'cancelled_bookings': 0, 'total_revenue': 0, 'avg_fare': 0}
            
            total_revenue = float(ksrtc['total_revenue']) + float(train['total_revenue']) + float(flight['total_revenue'])
            total_bookings = int(ksrtc['total_bookings']) + int(train['total_bookings']) + int(flight['total_bookings'])
            
            return jsonify({
                'success': True,
                'date': str(target_date),
                'total_revenue': total_revenue,
                'total_bookings': total_bookings,
                'ksrtc': {
                    'total_bookings': int(ksrtc['total_bookings']),
                    'confirmed_bookings': int(ksrtc['confirmed_bookings']),
                    'cancelled_bookings': int(ksrtc['cancelled_bookings']),
                    'total_revenue': float(ksrtc['total_revenue']),
                    'avg_fare': float(ksrtc['avg_fare'])
                },
                'train': {
                    'total_bookings': int(train['total_bookings']),
                    'confirmed_bookings': int(train['confirmed_bookings']),
                    'cancelled_bookings': int(train['cancelled_bookings']),
                    'total_revenue': float(train['total_revenue']),
                    'avg_fare': float(train['avg_fare'])
                },
                'flight': {
                    'total_bookings': int(flight['total_bookings']),
                    'confirmed_bookings': int(flight['confirmed_bookings']),
                    'cancelled_bookings': int(flight['cancelled_bookings']),
                    'total_revenue': float(flight['total_revenue']),
                    'avg_fare': float(flight['avg_fare'])
                },
                'top_users': top_users,
                'hourly_trend': hourly_trend
            })
        else:
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/user/expenses/daily', methods=['GET'])
@token_required
def get_user_daily_expenses(current_user):
    """Get user's daily expense breakdown"""
    try:
        from datetime import datetime, timedelta
        date_param = request.args.get('date')
        
        if date_param:
            target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
        else:
            target_date = datetime.now().date()
        
        user_id = current_user['user_id']
        
        # KSRTC expenses for the day
        ksrtc_expenses = execute_query("""
            SELECT 
                COUNT(*) as total_bookings,
                COUNT(CASE WHEN booking_status = 'Confirmed' THEN 1 END) as confirmed_bookings,
                COALESCE(SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END), 0) as total_spent
            FROM ksrtc_bookings
            WHERE user_id = %s AND DATE(journey_date) = %s
        """, (user_id, target_date), fetch=True)
        
        # Train expenses for the day
        train_expenses = execute_query("""
            SELECT 
                COUNT(*) as total_bookings,
                COUNT(CASE WHEN booking_status = 'Confirmed' THEN 1 END) as confirmed_bookings,
                COALESCE(SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END), 0) as total_spent
            FROM train_bookings
            WHERE user_id = %s AND DATE(journey_date) = %s
        """, (user_id, target_date), fetch=True)
        
        # Flight expenses for the day
        flight_expenses = execute_query("""
            SELECT 
                COUNT(*) as total_bookings,
                COUNT(CASE WHEN booking_status = 'Confirmed' THEN 1 END) as confirmed_bookings,
                COALESCE(SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END), 0) as total_spent
            FROM flight_bookings
            WHERE user_id = %s AND DATE(journey_date) = %s
        """, (user_id, target_date), fetch=True)
        
        # Recent bookings for this day
        recent_bookings = execute_query("""
            SELECT 
                'KSRTC' as type,
                booking_reference,
                boarding_stop as source,
                destination_stop as destination,
                journey_date,
                total_fare,
                booking_status,
                booking_time
            FROM ksrtc_bookings
            WHERE user_id = %s AND DATE(journey_date) = %s
            UNION ALL
            SELECT 
                'Train' as type,
                booking_reference,
                from_station as source,
                to_station as destination,
                journey_date,
                total_fare,
                booking_status,
                booking_time
            FROM train_bookings
            WHERE user_id = %s AND DATE(journey_date) = %s
            UNION ALL
            SELECT 
                'Flight' as type,
                booking_reference,
                from_airport as source,
                to_airport as destination,
                journey_date,
                total_fare,
                booking_status,
                booking_time
            FROM flight_bookings
            WHERE user_id = %s AND DATE(journey_date) = %s
            ORDER BY booking_time DESC
        """, (user_id, target_date, user_id, target_date, user_id, target_date), fetch=True) or []
        
        ksrtc = ksrtc_expenses[0] if ksrtc_expenses else {'total_bookings': 0, 'confirmed_bookings': 0, 'total_spent': 0}
        train = train_expenses[0] if train_expenses else {'total_bookings': 0, 'confirmed_bookings': 0, 'total_spent': 0}
        flight = flight_expenses[0] if flight_expenses else {'total_bookings': 0, 'confirmed_bookings': 0, 'total_spent': 0}
        
        total_spent = float(ksrtc['total_spent']) + float(train['total_spent']) + float(flight['total_spent'])
        total_bookings = int(ksrtc['total_bookings']) + int(train['total_bookings']) + int(flight['total_bookings'])
        
        return jsonify({
            'success': True,
            'date': str(target_date),
            'total_spent': total_spent,
            'total_bookings': total_bookings,
            'ksrtc': {
                'total_bookings': int(ksrtc['total_bookings']),
                'confirmed_bookings': int(ksrtc['confirmed_bookings']),
                'total_spent': float(ksrtc['total_spent'])
            },
            'train': {
                'total_bookings': int(train['total_bookings']),
                'confirmed_bookings': int(train['confirmed_bookings']),
                'total_spent': float(train['total_spent'])
            },
            'flight': {
                'total_bookings': int(flight['total_bookings']),
                'confirmed_bookings': int(flight['confirmed_bookings']),
                'total_spent': float(flight['total_spent'])
            },
            'recent_bookings': recent_bookings
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("  MULTI-MODAL TRANSPORT SYSTEM - Backend Server")
    print("="*60)
    print("\n✓ Server starting on http://localhost:5000")
    print("✓ CORS enabled for frontend access")
    print("\nAvailable endpoints:")
    print("  - POST /api/auth/signup")
    print("  - POST /api/auth/signin")
    print("  - POST /api/routes/search")
    print("  - GET  /api/routes/history")
    print("  - POST /api/bookings/create")
    print("  - GET  /api/bookings/my-bookings")
    print("  - GET  /api/admin/dashboard (Admin only)")
    print("\n" + "="*60 + "\n")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    except Exception as e:
        print(f"❌ Server error: {e}")
        import traceback
        traceback.print_exc()

