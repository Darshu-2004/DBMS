from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask import jsonify
from flask_mysqldb import MySQL #type:ignore
from flask_session import Session #type:ignore
import redis #type:ignore
import pickle
from datetime import datetime
from functools import wraps
import os # Import the os module to access environment variables
# Optional: color output in terminal for connection status
try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init()
    _HAS_COLORAMA = True
except Exception:
    _HAS_COLORAMA = False

# ------------------------------------------------------------------
# ---------- APP SETUP AND CONFIGURATION (USING ENV VARS) ----------
# ------------------------------------------------------------------

app = Flask(__name__)
# Read SECRET_KEY from environment variable, falling back to a default (for development)
app.secret_key = os.environ.get('SECRET_KEY', 'your-super-secret-key')

# --- Database Configuration (MySQL) ---
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'adminuser')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'adminpassword')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'transport')

# Attempt to initialize MySQL extension, but make this test-friendly: if a live
# database is not available at import time, set `mysql` to None and continue so
# tests can import the app without failing. We'll detect connectivity below.
mysql = None
mysql_connected = False

def try_init_mysql():
    """Attempt to initialize the MySQL extension and verify connectivity.

    Returns tuple (mysql_obj_or_none, connected_bool, message_str)
    """
    global mysql, mysql_connected
    try:
        mysql = MySQL(app)
        try:
            # mysql.connection requires an application context
            with app.app_context():
                cur = mysql.connection.cursor()
                cur.execute('SELECT 1')
                _ = cur.fetchone()
                cur.close()
            mysql_connected = True
            return mysql, True, 'Connected'
        except Exception as e:
            mysql_connected = False
            return mysql, False, f'Init failed: {e}'
    except Exception as e:
        mysql = None
        mysql_connected = False
        return None, False, f'Extension init error: {e}'

# Call once at startup to attempt connection but keep the app alive if it fails.
_mysql_obj, _mysql_ok, _mysql_msg = try_init_mysql()

# Control whether to show service badges/links in the UI (default: true)
SHOW_SERVICE_BADGES = os.environ.get('SHOW_SERVICE_BADGES', 'true').lower() in ('1', 'true', 'yes')

def ensure_mysql_connected():
    """Ensure mysql is initialized and connected. Called lazily from routes.

    Returns (mysql_obj, connected_bool)
    """
    global mysql, mysql_connected
    if mysql is not None and mysql_connected:
        return mysql, True
    # Try to (re-)initialize
    mysql, ok, msg = try_init_mysql()
    return mysql, ok


def get_enum_values(table, column):
    """Return a list of enum values for `table`.`column` or an empty list on error."""
    try:
        mysql_obj, ok = ensure_mysql_connected()
        if not ok or mysql_obj is None:
            return []
        cur = mysql.connection.cursor()
        # SHOW COLUMNS returns rows like (Field, Type, Null, Key, Default, Extra)
        cur.execute(f"SHOW COLUMNS FROM `{table}` LIKE %s", (column,))
        row = cur.fetchone()
        cur.close()
        if not row:
            return []
        type_def = row[1]  # e.g. "enum('a','b','c')"
        if not type_def.startswith('enum('):
            return []
        # extract values between the parentheses and split, handling quoted commas
        inner = type_def[type_def.find('(') + 1:type_def.rfind(')')]
        # inner is like: 'credit_card','debit_card','wallet'
        parts = []
        cur_val = []
        in_quote = False
        esc = False
        for ch in inner:
            if esc:
                cur_val.append(ch)
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == "'":
                in_quote = not in_quote
            elif ch == ',' and not in_quote:
                parts.append(''.join(cur_val))
                cur_val = []
            else:
                cur_val.append(ch)
        if cur_val:
            parts.append(''.join(cur_val))
        # strip surrounding quotes/spaces
        values = [p.strip().strip("'").strip() for p in parts if p is not None]
        return values
    except Exception:
        return []

# --- Session/Cache Configuration (Redis) ---
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
# The port must be an integer, so we cast it.
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379)) 

# We'll try to use Redis for sessions if available, otherwise fall back to
# filesystem sessions so the app can start without a Redis server.
r = None
redis_connected = False
try:
    redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, socket_connect_timeout=1)
    # quick ping to verify availability
    redis_conn.ping()
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_REDIS'] = redis_conn
    Session(app)
    r = redis_conn
    redis_connected = True
except Exception as e:
    # Redis not available; fall back to filesystem session storage to allow
    # local development and testing without Redis.
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)
    r = None
    redis_connected = False
    _redis_err = str(e)

# Print friendly startup status in the terminal with icons/colors
def _print_status(name, ok, extra=''):
    if _HAS_COLORAMA:
        green = Fore.GREEN + Style.BRIGHT
        red = Fore.RED + Style.BRIGHT
        reset = Style.RESET_ALL
    else:
        green = red = reset = ''
    icon = '✅' if ok else '❌'
    color = green if ok else red
    print(f"{color}{icon} {name}: {'OK' if ok else 'NOT AVAILABLE'} {extra}{reset}")

_print_status('Redis', redis_connected, f'({_redis_err})' if (not redis_connected and '_redis_err' in globals()) else '')
_print_status('MySQL', mysql_connected, f'({_mysql_msg})' if (not mysql_connected and '_mysql_msg' in globals()) else '')

# ------------------------------------------------------------------
# ---------- AUTH AND ROLE DECORATOR ----------
# ------------------------------------------------------------------

def login_required(role=None):
    """
    Decorator to ensure a user is logged in and optionally has a specific role.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            # If not logged in, send to login page
            if 'role' not in session:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('login'))
            # If a specific role is required and user does not have it,
            # redirect back to dashboard and show a helpful message instead
            # of returning a bare 403 response which looks like an error page.
            if role and session.get('role') != role:
                flash(f'Access denied. Required role: {role}. Current role: {session.get("role")}', 'error')
                return redirect(url_for('dashboard'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

# ------------------------------------------------------------------
# ---------- AUTH ROUTES (LOGIN/LOGOUT) ----------
# ------------------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login by verifying credentials against the User table.

    NOTE: Passwords are stored in plaintext in the database for this project
    (per repository constraints). This handler therefore performs a plain
    equality check against the `password_hash` column. Do NOT copy this
    pattern to production code — always store hashed passwords.
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Ensure MySQL is available before attempting authentication.
        mysql_obj, mysql_ok = ensure_mysql_connected()
        if not mysql_ok or mysql_obj is None:
            flash('Authentication currently unavailable (database offline).', 'error')
            return render_template('login.html')

        try:
            cur = mysql.connection.cursor()
            # Allow login by username or email
            cur.execute('SELECT user_id, email, user_type, password_hash FROM User WHERE name = %s OR email = %s', (username, username))
            user = cur.fetchone()
            cur.close()

            if user and user[3] is not None and user[3] == password:
                # Successful authentication (plain-text comparison)
                session['logged_in'] = True
                session['user_id'] = user[0]
                session['email'] = user[1]
                session['username'] = username
                session['role'] = user[2]
                flash(f'Logged in successfully as {username} ({session["role"]})', 'success')
                return redirect(url_for('dashboard'))
            else:
                # Generic failure message to avoid leaking which part failed
                flash('Login failed. Invalid username or password.', 'error')

        except Exception as e:
            # DB error while attempting login
            flash(f'Login error: {e}', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Handles user logout and session clearing."""
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('email', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Public registration endpoint for new users.

    Users created here are given the default role 'passenger' as requested.
    Passwords are stored in plaintext in this project (explicitly intended
    for the exercise). The route will auto-login the new user after
    successful creation.
    """
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not name or not email or not password:
            flash('Please provide name, email and password.', 'error')
            return render_template('register.html')

        # Ensure DB available
        mysql_obj, mysql_ok = ensure_mysql_connected()
        if not mysql_ok or mysql_obj is None:
            flash('Registration currently unavailable (database offline).', 'error')
            return render_template('register.html')

        try:
            cur = mysql.connection.cursor()
            # Check for existing user by name or email
            cur.execute('SELECT user_id FROM User WHERE name = %s OR email = %s', (name, email))
            exists = cur.fetchone()
            if exists:
                cur.close()
                flash('A user with that username or email already exists. Please log in.', 'error')
                return redirect(url_for('login'))

            # Insert new user as passenger; store password in plaintext per project rules
            cur.execute('INSERT INTO User (name, email, password_hash, user_type) VALUES (%s, %s, %s, %s)',
                        (name, email, password, 'passenger'))
            mysql.connection.commit()

            # Fetch the created user id
            cur.execute('SELECT user_id FROM User WHERE email = %s', (email,))
            user = cur.fetchone()
            cur.close()

            if user:
                # Auto-login the new user
                session['logged_in'] = True
                session['user_id'] = user[0]
                session['email'] = email
                session['username'] = name
                session['role'] = 'passenger'
                flash('Account created and logged in as passenger.', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Registration succeeded but could not log in. Please try logging in manually.', 'info')
                return redirect(url_for('login'))

        except Exception as e:
            try:
                mysql.connection.rollback()
            except Exception:
                pass
            flash(f'Registration error: {e}', 'error')

    return render_template('register.html')

@app.route('/')
def index():
    """Default route redirects to login or dashboard."""
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required()
def dashboard():
    """Dispatch to a role-specific dashboard template.

    This renders a different template for admin, operator, and passenger users.
    Keeping separate templates makes it easier to customize each dashboard later.
    """
    role = session.get('role')

    # Prepare some quick counts/summary info for each role. If the database
    # isn't connected, show 'N/A' so the dashboard still renders for tests.
    counts = {}
    if mysql is not None and mysql_connected:
        try:
            cur = mysql.connection.cursor()
            if role == 'admin':
                cur.execute('SELECT COUNT(*) FROM User')
                counts['users'] = cur.fetchone()[0]
                cur.execute('SELECT COUNT(*) FROM Route')
                counts['routes'] = cur.fetchone()[0]
                cur.execute('SELECT COUNT(*) FROM Vehicle')
                counts['vehicles'] = cur.fetchone()[0]
            elif role == 'operator':
                cur.execute('SELECT COUNT(*) FROM Trip')
                counts['trips'] = cur.fetchone()[0]
            else:
                # passenger
                try:
                    cur.execute('SELECT COUNT(*) FROM Ticket WHERE user_id=%s', (session.get('user_id'),))
                    counts['my_tickets'] = cur.fetchone()[0]
                except Exception:
                    counts['my_tickets'] = 'N/A'
            cur.close()
        except Exception:
            # If any DB error happens, fall back to N/A values
            counts = {k: 'N/A' for k in ['users', 'routes', 'vehicles', 'trips', 'my_tickets']}
    else:
        # DB not connected; return 'N/A' for counts
        counts = {k: 'N/A' for k in ['users', 'routes', 'vehicles', 'trips', 'my_tickets']}

    # Render role-specific template and include counts and connection status so
    # templates can show a success message if services are connected.
    if role == 'admin':
        return render_template('dashboard_admin.html', role=role, counts=counts, db_connected=mysql_connected, redis_connected=redis_connected)
    elif role == 'operator':
        return render_template('dashboard_operator.html', role=role, counts=counts, db_connected=mysql_connected, redis_connected=redis_connected)
    else:
        return render_template('dashboard_passenger.html', role=role, counts=counts, db_connected=mysql_connected, redis_connected=redis_connected)

# ------------------------------------------------------------------
# ---------- USERS (Admin Only) ----------
# ------------------------------------------------------------------

@app.route('/users')
@login_required('admin')
def users():
    """View all users."""
    cur = mysql.connection.cursor()
    cur.execute('SELECT user_id, name, email, user_type FROM User')
    users = cur.fetchall()
    cur.close()
    return render_template('users.html', users=users)

@app.route('/create_user', methods=['GET', 'POST'])
@login_required('admin')
def create_user():
    """Create a new user."""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password_hash = request.form['password_hash'] # NOTE: Password should be hashed in real app
        user_type = request.form['user_type']
        
        # In a real application, you would hash the password before inserting.
        # For simplicity, we store the raw password here.
        cur = mysql.connection.cursor()
        try:
            cur.execute('INSERT INTO User (name, email, password_hash, user_type) VALUES (%s, %s, %s, %s)',
                        (name, email, password_hash, user_type))
            mysql.connection.commit()
            flash(f'User {name} created successfully!', 'success')
            return redirect(url_for('users'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error creating user: {e}', 'error')
        finally:
            cur.close()

    return render_template('create_user.html')

# ------------------------------------------------------------------
# ---------- STATIONS (Admin Only) ----------
# ------------------------------------------------------------------

@app.route('/stations')
@login_required('admin')
def stations():
    """View all stations."""
    cur = mysql.connection.cursor()
    # Assuming station_id, name, location, type
    cur.execute('SELECT station_id, name, location, type FROM Station')
    stations = cur.fetchall()
    cur.close()
    # Note: stations.html needs a 'border="1"' or similar for visibility
    return render_template('stations.html', stations=stations)

@app.route('/create_station', methods=['GET', 'POST'])
@login_required('admin')
def create_station():
    """Create a new station."""
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        station_type = request.form['type']
        
        cur = mysql.connection.cursor()
        try:
            cur.execute('INSERT INTO Station (name, location, type) VALUES (%s, %s, %s)',
                        (name, location, station_type))
            mysql.connection.commit()
            flash('Station created!', 'success')
            return redirect(url_for('stations'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error creating station: {e}', 'error')
        finally:
            cur.close()

    return render_template('create_station.html')

# ------------------------------------------------------------------
# ---------- ROUTES (Admin Only) ----------
# ------------------------------------------------------------------

@app.route('/routes')
@login_required('admin')
def routes():
    """View all routes."""
    # Using a join to show station names instead of IDs for better readability
    query = """
    SELECT 
        R.route_id, R.mode, 
        OS.name AS origin_name, 
        DS.name AS destination_name, 
        R.distance_km
    FROM Route R
    JOIN Station OS ON R.origin_station_id = OS.station_id
    JOIN Station DS ON R.destination_station_id = DS.station_id
    """
    cur = mysql.connection.cursor()
    cur.execute(query)
    routes = cur.fetchall()
    cur.close()
    return render_template('routes.html', routes=routes)

@app.route('/create_route', methods=['GET', 'POST'])
@login_required('admin')
def create_route():
    """Create a new route."""
    if request.method == 'POST':
        mode = request.form['mode']
        origin_station_id = request.form['origin_station_id']
        destination_station_id = request.form['destination_station_id']
        distance_km = request.form['distance_km']
        
        cur = mysql.connection.cursor()
        try:
            cur.execute('INSERT INTO Route (mode, origin_station_id, destination_station_id, distance_km) VALUES (%s, %s, %s, %s)',
                        (mode, origin_station_id, destination_station_id, distance_km))
            mysql.connection.commit()
            flash('Route created!', 'success')
            return redirect(url_for('routes'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error creating route: {e}', 'error')
        finally:
            cur.close()

    return render_template('create_route.html')

# ------------------------------------------------------------------
# ---------- VEHICLES (Admin/Operator) ----------
# ------------------------------------------------------------------

@app.route('/vehicles')
@login_required() # Accessible by all logged in users
def vehicles():
    """View all vehicles (and which route they are assigned to)."""
    # Join with Route for better display
    query = """
    SELECT 
        V.vehicle_id, R.route_id, V.type, V.capacity, V.registration_number, V.status
    FROM Vehicle V
    LEFT JOIN Route R ON V.route_id = R.route_id
    """
    cur = mysql.connection.cursor()
    cur.execute(query)
    vehicles = cur.fetchall()
    cur.close()
    return render_template('vehicles.html', vehicles=vehicles)

@app.route('/create_vehicle', methods=['GET', 'POST'])
@login_required('admin') # Only admin can create vehicles
def create_vehicle():
    """Create a new vehicle."""
    if request.method == 'POST':
        route_id = request.form['route_id'] if request.form.get('route_id') else None
        vehicle_type = request.form['type']
        capacity = request.form['capacity']
        registration_number = request.form['registration_number']
        status = request.form['status']
        
        cur = mysql.connection.cursor()
        try:
            cur.execute('INSERT INTO Vehicle (route_id, type, capacity, registration_number, status) VALUES (%s, %s, %s, %s, %s)',
                        (route_id, vehicle_type, capacity, registration_number, status))
            mysql.connection.commit()
            flash('Vehicle created!', 'success')
            return redirect(url_for('vehicles'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error creating vehicle: {e}', 'error')
        finally:
            cur.close()

    return render_template('create_vehicle.html')

# ------------------------------------------------------------------
# ---------- TRIPS (Operator Only) ----------
# ------------------------------------------------------------------

@app.route('/trips')
@login_required('operator')
def trips():
    """View all scheduled trips."""
    # Join with Vehicle and Route for better display
    query = """
    SELECT 
        T.trip_id, V.registration_number, R.route_id, T.departure_time, T.arrival_time, T.status
    FROM Trip T
    JOIN Vehicle V ON T.vehicle_id = V.vehicle_id
    JOIN Route R ON T.route_id = R.route_id
    """
    cur = mysql.connection.cursor()
    cur.execute(query)
    trips = cur.fetchall()
    cur.close()
    return render_template('trips.html', trips=trips)

@app.route('/create_trip', methods=['GET', 'POST'])
@login_required('operator')
def create_trip():
    """Create a new trip."""
    if request.method == 'POST':
        vehicle_id = request.form['vehicle_id']
        route_id = request.form['route_id']
        departure_time = request.form['departure_time']
        arrival_time = request.form['arrival_time']
        status = request.form['status']
        
        cur = mysql.connection.cursor()
        try:
            cur.execute('INSERT INTO Trip (vehicle_id, route_id, departure_time, arrival_time, status) VALUES (%s, %s, %s, %s, %s)',
                        (vehicle_id, route_id, departure_time, arrival_time, status))
            mysql.connection.commit()
            flash('Trip created!', 'success')
            return redirect(url_for('trips'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error creating trip: {e}', 'error')
        finally:
            cur.close()

    return render_template('create_trip.html')

# ------------------------------------------------------------------
# ---------- TICKETS (Passenger/Operator) ----------
# ------------------------------------------------------------------

@app.route('/tickets')
@login_required() # Accessible by all logged in users for now, typically restricted to passenger's own tickets
def tickets():
    """View tickets. Operators see all, Passengers see their own."""
    cur = mysql.connection.cursor()
    
    if session['role'] == 'passenger':
        # Passengers only see their own tickets
        query = """
        SELECT T.ticket_id, U.name, T.trip_id, T.purchase_time, T.seat_number, T.status
        FROM Ticket T
        JOIN User U ON T.user_id = U.user_id
        WHERE T.user_id = %s
        """
        cur.execute(query, (session['user_id'],))
    else:
        # Admins/Operators see all tickets
        query = """
        SELECT T.ticket_id, U.name, T.trip_id, T.purchase_time, T.seat_number, T.status
        FROM Ticket T
        JOIN User U ON T.user_id = U.user_id
        """
        cur.execute(query)

    tickets = cur.fetchall()
    cur.close()
    return render_template('tickets.html', tickets=tickets)

@app.route('/book_ticket', methods=['GET', 'POST'])
@login_required('passenger')
def book_ticket():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        user_id = session['user_id']
        trip_id = request.form['trip_id']
        purchase_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        seat_number = request.form['seat_number']
        status = 'Booked'
        try:
            cur.execute(
                'INSERT INTO Ticket (user_id, trip_id, purchase_time, seat_number, status) VALUES (%s, %s, %s, %s, %s)',
                (user_id, trip_id, purchase_time, seat_number, status)
            )
            mysql.connection.commit()
            flash('Ticket booked successfully!', 'success')
            return redirect(url_for('tickets'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error booking ticket: {e}', 'error')
        # Fetch trips again to refill the dropdown after error
        cur.execute("SELECT trip_id FROM trip WHERE status!='cancelled'")
        # Try both fetch formats for Jinja
        trips = cur.fetchall()
        # For dict: {% for trip in trips %}<option value="{{ trip['trip_id'] }}">
        # For tuple: {% for trip in trips %}<option value="{{ trip[0] }}">
        return render_template('book_ticket.html', trips=trips)
    else:
        cur.execute("SELECT trip_id FROM trip WHERE status!='cancelled'")
        trips = cur.fetchall()
        return render_template('book_ticket.html', trips=trips)

# ------------------------------------------------------------------
# ---------- PAYMENTS (Passenger Only) ----------
# ------------------------------------------------------------------

@app.route('/payments')
@login_required('passenger')
def payments():
    """View payments made by the logged-in user."""
    query = """
    SELECT P.payment_id, P.ticket_id, P.amount, P.payment_time, P.method, P.status
    FROM Payment P
    JOIN Ticket T ON P.ticket_id = T.ticket_id
    WHERE T.user_id = %s
    """
    cur = mysql.connection.cursor()
    cur.execute(query, (session['user_id'],))
    payments = cur.fetchall()
    cur.close()
    return render_template('payments.html', payments=payments)

@app.route('/pay', methods=['GET', 'POST'])
@login_required('passenger')
def pay():
    """Make a payment for a ticket."""
    # Dynamically fetch allowed methods from the DB enum; fall back to a
    # sensible default list of canonical DB values if the DB is unavailable
    # or the enum cannot be read.
    enum_vals = get_enum_values('Payment', 'method')
    if not enum_vals:
        # fallback to canonical values present in the DDL/DML
        enum_vals = ['credit_card', 'debit_card', 'wallet', 'cash']

    # Map DB enum tokens to friendly labels for display. If you want custom
    # labels, extend this mapping; by default we Title-case and replace
    # underscores.
    friendly_map = {
        'credit_card': 'Credit Card',
        'debit_card': 'Debit Card',
        'wallet': 'Wallet/UPI',
        'cash': 'Cash'
    }
    methods_choices = [(v, friendly_map.get(v, v.replace('_', ' ').title())) for v in enum_vals]
    if request.method == 'POST':
        # Temporary debugging: log the raw POST payload so we can see what
        # the client is sending that causes enum/truncation errors.
        try:
            app.logger.info('PAY POST payload: %s', dict(request.form))
        except Exception:
            print('PAY POST payload (could not use logger):', request.form)
        # Basic validation and sanitization to avoid DB errors (e.g., enum/varchar truncation)
        ticket_id_raw = request.form.get('ticket_id', '').strip()
        amount_raw = request.form.get('amount', '').strip()
        method = request.form.get('method', '').strip()
        status = request.form.get('status', 'Completed').strip() or 'Completed'

        # Validate ticket_id and amount
        try:
            ticket_id = int(ticket_id_raw)
        except Exception:
            flash('Invalid ticket id.', 'error')
            return render_template('pay.html', methods_choices=methods_choices)

        try:
            amount = float(amount_raw)
            if amount <= 0:
                raise ValueError()
        except Exception:
            flash('Invalid amount value.', 'error')
            return render_template('pay.html', methods_choices=methods_choices)

        # Restrict payment method to the enum values fetched from the DB
        allowed_methods = tuple(v for v, _ in methods_choices)

        # If the posted value is a friendly label (e.g. 'Card' or 'Credit Card'),
        # try to map it to the canonical DB token. This handles stale clients or
        # manual POSTs that send display labels instead of DB values.
        if method not in allowed_methods:
            posted = method.strip()
            mapped = None
            for val, label in methods_choices:
                if posted.lower() == val.lower() or posted.lower() == label.lower():
                    mapped = val
                    break
                # also accept common variants (e.g., 'card' -> 'credit_card')
                if posted.lower().replace(' ', '') == label.lower().replace(' ', ''):
                    mapped = val
                    break

            if mapped:
                # replace method with canonical token
                method = mapped
            else:
                # Heuristic fallbacks for common short labels (Card, Cash, UPI, Netbanking)
                p = posted.lower()
                if 'debit' in p:
                    # map to debit_card if available
                    if any(v == 'debit_card' for v, _ in methods_choices):
                        mapped = 'debit_card'
                elif ('credit' in p) or ('card' in p and 'debit' not in p):
                    if any(v == 'credit_card' for v, _ in methods_choices):
                        mapped = 'credit_card'
                elif 'cash' in p:
                    if any(v == 'cash' for v, _ in methods_choices):
                        mapped = 'cash'
                elif 'upi' in p or 'wallet' in p or 'netbank' in p:
                    if any(v == 'wallet' for v, _ in methods_choices):
                        mapped = 'wallet'

                if mapped:
                    method = mapped
                else:
                    # As a last-resort normalization attempt, convert common
                    # display labels into a canonical token (e.g. "Credit Card" -> "credit_card").
                    norm = posted.lower().strip().replace(' ', '_')
                    if norm in allowed_methods:
                        method = norm
                    else:
                        # still invalid after attempts to map/normalize
                        flash('Invalid payment method. Please choose a supported method.', 'error')
                        return render_template('pay.html', methods_choices=methods_choices)

        # Ensure DB available
        mysql_obj, mysql_ok = ensure_mysql_connected()
        if not mysql_ok or mysql_obj is None:
            flash('Database is not available; cannot process payment.', 'error')
            return render_template('pay.html', methods_choices=methods_choices)

        payment_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cur = mysql.connection.cursor()
        try:
            # Debugging: log the canonical values we are about to insert
            try:
                app.logger.info('PAY INSERT values: ticket=%s amount=%s method=%s status=%s', ticket_id, amount, method, status)
            except Exception:
                print('PAY INSERT values:', ticket_id, amount, method, status)
            cur.execute(
                'INSERT INTO Payment (ticket_id, amount, payment_time, method, status) VALUES (%s,%s,%s,%s,%s)',
                (ticket_id, amount, payment_time, method, status)
            )

            # Optionally update ticket status to paid
            cur.execute('UPDATE Ticket SET status = %s WHERE ticket_id = %s', ('Paid', ticket_id))

            mysql.connection.commit()
            flash('Payment made and ticket marked as Paid!', 'success')
            return redirect(url_for('payments'))
        except Exception as e:
            mysql.connection.rollback()
            # Provide a more helpful error if it's a known truncation/enum issue
            msg = str(e)
            if 'Data truncated for column' in msg or '1265' in msg:
                flash('Payment failed: selected method is not compatible with the database schema.', 'error')
            else:
                flash(f'Error processing payment: {e}', 'error')
        finally:
            cur.close()

    return render_template('pay.html', methods_choices=methods_choices)

# ------------------------------------------------------------------
# ---------- ANNOUNCEMENTS (View for all, Create/Edit/Delete for Operator) ----------
# ------------------------------------------------------------------

@app.route('/announcements')
@login_required() # All logged-in users can view
def announcements():
    """View all announcements."""
    cur = mysql.connection.cursor()
    cur.execute('SELECT announcement_id, message, announcement_time FROM Announcement ORDER BY announcement_time DESC')
    announcements = cur.fetchall()
    cur.close()
    return render_template('announcements.html', announcements=announcements)

@app.route('/create_announcement', methods=['GET', 'POST'])
@login_required('operator')
def create_announcement():
    """Create a new announcement."""
    if request.method == 'POST':
        message = request.form['message']
        # Use server time if announcement_time is not provided or is empty
        announcement_time = request.form.get('announcement_time') or datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        
        cur = mysql.connection.cursor()
        try:
            cur.execute('INSERT INTO Announcement (message, announcement_time) VALUES (%s,%s)', (message, announcement_time))
            mysql.connection.commit()
            flash('Announcement posted!', 'success')
            return redirect(url_for('announcements'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error posting announcement: {e}', 'error')
        finally:
            cur.close()

    return render_template('create_announcement.html')

@app.route('/edit_announcement/<int:announcement_id>', methods=['GET', 'POST'])
@login_required('operator')
def edit_announcement(announcement_id):
    """Edit an existing announcement."""
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        message = request.form['message']
        # Use current server time for update timestamp
        announcement_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            cur.execute('UPDATE Announcement SET message=%s, announcement_time=%s WHERE announcement_id=%s',
                        (message, announcement_time, announcement_id))
            mysql.connection.commit()
            flash('Announcement updated!', 'success')
            return redirect(url_for('announcements'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error updating announcement: {e}', 'error')
        finally:
            cur.close()
            
    # GET request: fetch current announcement data
    cur.execute('SELECT announcement_id, message, announcement_time FROM Announcement WHERE announcement_id=%s', (announcement_id,))
    announcement = cur.fetchone()
    cur.close()
    
    # Check if announcement exists before rendering
    if not announcement:
        flash('Announcement not found.', 'error')
        return redirect(url_for('announcements'))
        
    # Assuming edit_announcement.html exists to handle the form
    return render_template('edit_announcement.html', announcement=announcement) 

@app.route('/delete_announcement/<int:announcement_id>')
@login_required('operator')
def delete_announcement(announcement_id):
    """Delete an announcement."""
    cur = mysql.connection.cursor()
    try:
        cur.execute('DELETE FROM Announcement WHERE announcement_id=%s', (announcement_id,))
        mysql.connection.commit()
        flash('Announcement deleted!', 'info')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error deleting announcement: {e}', 'error')
    finally:
        cur.close()
    return redirect(url_for('announcements'))


# ------------------------------------------------------------------
# ---------- HEALTH CHECK (machine-readable) ------------------------
# ------------------------------------------------------------------
@app.route('/health')
def health():
    """Return machine-readable service health (JSON).

    Status code: 200 when all services OK, 503 otherwise.
    """
    # Check MySQL (try a lazy reconnect)
    mysql_obj, mysql_ok = ensure_mysql_connected()

    # Check Redis
    redis_ok = False
    redis_err = None
    try:
        if r:
            r.ping()
            redis_ok = True
    except Exception as e:
        redis_ok = False
        redis_err = str(e)

    payload = {
        'mysql': bool(mysql_ok),
        'redis': bool(redis_ok),
        'mysql_msg': None if mysql_ok else 'unavailable',
        'redis_msg': redis_err,
        'timestamp': datetime.now().isoformat()
    }
    status = 200 if (mysql_ok and redis_ok) else 503
    return jsonify(payload), status

# ------------------------------------------------------------------
# ---------- APP RUNNER ----------
# ------------------------------------------------------------------

if __name__ == '__main__':
    # Running in debug mode, in production this is often managed by a WSGI server
    app.run(debug=True)


@app.context_processor
def inject_now():
    """Provide `now` to templates for footers and timestamps."""
    # Expose connection status flags to templates so they can show success
    # messages or badges when DB/Redis are available.
    return {
        'now': datetime.now(),
        'db_connected': mysql_connected,
        'redis_connected': redis_connected,
        'show_service_badges': SHOW_SERVICE_BADGES,
    }
