from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_session import Session
import redis
import pickle
from datetime import datetime
import os # Import the os module to access environment variables

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
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'transportsystem')
mysql = MySQL(app)

# --- Session/Cache Configuration (Redis) ---
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
# The port must be an integer, so we cast it.
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379)) 

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
Session(app)
# Global Redis connection for caching
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

# ------------------------------------------------------------------
# ---------- AUTH AND ROLE DECORATOR ----------
# ------------------------------------------------------------------

def login_required(role=None):
    """
    Decorator to ensure a user is logged in and optionally has a specific role.
    """
    def wrapper(fn):
        def decorated_view(*args, **kwargs):
            if 'role' not in session:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('login'))
            if role and session['role'] != role:
                flash(f'Access denied. Required role: {role}. Current role: {session["role"]}', 'error')
                return "Forbidden", 403
            return fn(*args, **kwargs)
        # Flask requires the decorated function to retain the original name
        decorated_view.__name__ = fn.__name__
        return decorated_view
    return wrapper

# ------------------------------------------------------------------
# ---------- AUTH ROUTES (LOGIN/LOGOUT) ----------
# ------------------------------------------------------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login by checking a mocked database/user table."""
    if request.method == 'POST':
        username = request.form['username']
        
        # In a real app, this would check password/hash as well.
        # Here we mock user/role look-up.
        cur = mysql.connection.cursor()
        cur.execute('SELECT user_id, email, user_type FROM User WHERE name = %s', [username])
        user = cur.fetchone()
        cur.close()

        if user:
            # Assuming user[2] is the user_type (e.g., 'admin', 'operator', 'passenger')
            session['logged_in'] = True
            session['user_id'] = user[0]
            session['email'] = user[1]
            session['role'] = user[2]
            flash(f'Logged in successfully as {username} ({session["role"]})', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. User not found.', 'error')

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

@app.route('/')
def index():
    """Default route redirects to login or dashboard."""
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required()
def dashboard():
    """User-specific dashboard based on role."""
    return render_template('dashboard.html', role=session['role'])

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
    if request.method == 'POST':
        ticket_id = request.form['ticket_id']
        amount = request.form['amount']
        payment_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Use server time
        method = request.form['method']
        status = 'Completed' # Default status
        
        cur = mysql.connection.cursor()
        try:
            cur.execute('INSERT INTO Payment (ticket_id, amount, payment_time, method, status) VALUES (%s,%s,%s,%s,%s)',
                        (ticket_id, amount, payment_time, method, status))
            
            # Optionally update ticket status to paid
            cur.execute('UPDATE Ticket SET status = %s WHERE ticket_id = %s', ('Paid', ticket_id))

            mysql.connection.commit()
            flash('Payment made and ticket marked as Paid!', 'success')
            return redirect(url_for('payments'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error processing payment: {e}', 'error')
        finally:
            cur.close()

    return render_template('pay.html')

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
# ---------- APP RUNNER ----------
# ------------------------------------------------------------------

if __name__ == '__main__':
    # Running in debug mode, in production this is often managed by a WSGI server
    app.run(debug=True)
