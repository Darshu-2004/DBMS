# MULTI-MODAL TRANSPORT SYSTEM
## Database Management System Mini Project

---

## TEAM DETAILS

**Project Title:** Multi-Modal Transport System with Real-Time Tracking and Analytics

**Team Members:**
- [Name 1] - [USN]
- [Name 2] - [USN]
- [Name 3] - [USN]
- [Name 4] - [USN]

**Institution:** [Your College Name]
**Department:** Computer Science & Engineering
**Course:** Database Management Systems (UE23CS351A)
**Academic Year:** 2024-25

---

## 1. ABSTRACT

The Multi-Modal Transport System is a comprehensive web-based application designed to integrate various modes of transportation including KSRTC buses, trains, and flights into a unified booking platform. The system provides users with the ability to search, compare, and book tickets across different transport modes while offering administrators powerful analytics and revenue tracking capabilities.

### Key Features:
- **Multi-Modal Integration:** Seamless booking across KSRTC, trains, and flights
- **Real-Time Tracking:** Live location tracking for KSRTC buses
- **User Management:** Secure authentication with role-based access (Admin/User)
- **Expense Tracking:** Daily and monthly expense analytics for users
- **Revenue Analytics:** Comprehensive revenue tracking and reporting for administrators
- **Seat Management:** Dynamic seat allocation and availability checking
- **Responsive UI:** Modern, gradient-based interface with interactive dashboards

### Technologies Used:
- Backend: Flask (Python)
- Frontend: HTML5, CSS3, JavaScript
- Database: MySQL 8.0
- Spatial Data: PostGIS for location tracking
- Charts: Chart.js for data visualization

---

## 2. USER REQUIREMENT SPECIFICATION

### 2.1 Functional Requirements

#### For Regular Users:
1. **Account Management**
   - User registration with email verification
   - Secure login/logout functionality
   - Profile management

2. **Booking Operations**
   - Search for KSRTC buses by route and date
   - Search for trains by station codes and date
   - Search for flights by airport codes and date
   - View available seats in real-time
   - Book tickets with seat selection
   - Cancel bookings
   - Download mobile tickets

3. **Expense Tracking**
   - View daily expenses breakdown by transport mode
   - View monthly expense trends
   - Export expense reports

4. **Tracking Features**
   - Track live location of KSRTC buses
   - View booking history
   - Access digital tickets

#### For Administrators:
1. **Revenue Management**
   - View daily revenue breakdown (KSRTC/Train/Flight)
   - Identify top spenders
   - Analyze peak booking hours
   - Generate revenue reports

2. **Analytics Dashboard**
   - Transport mode usage statistics
   - Popular routes analysis
   - Booking trends visualization
   - User activity monitoring

3. **System Management**
   - View all bookings
   - Monitor system status
   - Access user statistics

### 2.2 Non-Functional Requirements

1. **Security**
   - Password hashing using bcrypt
   - Session-based authentication
   - SQL injection prevention through parameterized queries
   - XSS protection

2. **Performance**
   - Response time < 2 seconds for search queries
   - Support for concurrent bookings
   - Efficient seat locking mechanism

3. **Scalability**
   - Modular architecture for easy expansion
   - Support for adding new transport modes
   - Database indexing for faster queries

4. **Usability**
   - Intuitive user interface
   - Responsive design for mobile devices
   - Clear error messages and validation

---

## 3. SOFTWARE & TOOLS USED

### 3.1 Development Environment
| Tool/Software | Version | Purpose |
|--------------|---------|---------|
| Python | 3.10+ | Backend development |
| Flask | 2.3.0 | Web framework |
| MySQL | 8.0 | Primary database |
| PostGIS | 3.0+ | Spatial data handling |
| VS Code | Latest | Code editor |
| Git | Latest | Version control |

### 3.2 Python Libraries
```python
Flask==2.3.0
Flask-CORS==4.0.0
mysql-connector-python==8.0.33
bcrypt==4.0.1
psycopg2-binary==2.9.6
python-dotenv==1.0.0
```

### 3.3 Frontend Technologies
- **HTML5:** Structure and semantic markup
- **CSS3:** Styling with gradients and animations
- **JavaScript (ES6+):** Dynamic interactions
- **Chart.js:** Data visualization
- **Google Fonts:** Typography (Poppins)

---

## 4. ER DIAGRAM

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│    USERS    │         │   BOOKINGS   │         │   ROUTES    │
├─────────────┤         ├──────────────┤         ├─────────────┤
│ user_id (PK)│◄────────┤ booking_id(PK)│         │ route_id(PK)│
│ username    │         │ user_id (FK) │         │ source      │
│ email       │         │ booking_type │         │ destination │
│ password    │         │ journey_date │         │ distance    │
│ full_name   │         │ total_fare   │         └─────────────┘
│ user_type   │         │ status       │                │
└─────────────┘         └──────────────┘                │
                               │                        │
                        ┌──────┴──────┐                │
                        ▼              ▼                ▼
              ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
              │ KSRTC_       │  │ TRAIN_       │  │ FLIGHT_      │
              │ BOOKINGS     │  │ BOOKINGS     │  │ BOOKINGS     │
              ├──────────────┤  ├──────────────┤  ├──────────────┤
              │ booking_id   │  │ booking_id   │  │ booking_id   │
              │ schedule_id  │  │ train_id     │  │ flight_id    │
              │ seat_numbers │  │ pnr_number   │  │ seat_numbers │
              │ total_fare   │  │ coach_type   │  │ class_type   │
              └──────────────┘  └──────────────┘  └──────────────┘
                     │                 │                  │
                     ▼                 ▼                  ▼
              ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
              │ KSRTC_SEATS  │  │ TRAIN_COACHES│  │ FLIGHT_SEATS │
              ├──────────────┤  ├──────────────┤  ├──────────────┤
              │ seat_id (PK) │  │ coach_id(PK) │  │ seat_id (PK) │
              │ bus_id (FK)  │  │ train_id(FK) │  │ flight_id(FK)│
              │ seat_number  │  │ coach_type   │  │ seat_number  │
              │ is_available │  │ total_seats  │  │ class_type   │
              └──────────────┘  └──────────────┘  └──────────────┘

┌──────────────────┐         ┌─────────────────┐
│ BOOKING_ACTIVITY │         │ EXPENSES        │
│ _LOG (Triggers)  │         │                 │
├──────────────────┤         ├─────────────────┤
│ log_id (PK)      │         │ expense_id (PK) │
│ booking_type     │         │ user_id (FK)    │
│ booking_ref      │         │ expense_date    │
│ user_id (FK)     │         │ amount          │
│ action_type      │         │ transport_mode  │
│ old_status       │         └─────────────────┘
│ new_status       │
│ log_timestamp    │
└──────────────────┘
```

**Key Relationships:**
- Users (1) ──── (M) Bookings
- KSRTC_Bookings (1) ──── (M) KSRTC_Seats
- Train_Bookings (1) ──── (M) Train_Coaches
- Flight_Bookings (1) ──── (M) Flight_Seats
- Bookings (1) ──── (1) Expenses

---

## 5. RELATIONAL SCHEMA

### 5.1 Core Tables

**USERS**
```
users(user_id, username, email, password_hash, full_name, phone_number, 
      created_at, last_login, is_active, user_type)
Primary Key: user_id
Unique: username, email
```

**KSRTC_BOOKINGS**
```
ksrtc_bookings(booking_id, user_id, schedule_id, booking_reference, 
               journey_date, passenger_name, passenger_age, passenger_gender,
               seat_numbers, total_fare, booking_status, booking_time)
Primary Key: booking_id
Foreign Key: user_id REFERENCES users(user_id)
Foreign Key: schedule_id REFERENCES ksrtc_schedules(schedule_id)
```

**TRAIN_BOOKINGS**
```
train_bookings(booking_id, user_id, train_id, pnr_number, journey_date,
               source_station, destination_station, coach_type, seat_count,
               berth_preference, passenger_names, total_fare, booking_status)
Primary Key: booking_id
Foreign Key: user_id REFERENCES users(user_id)
Foreign Key: train_id REFERENCES trains(train_id)
```

**FLIGHT_BOOKINGS**
```
flight_bookings(booking_id, user_id, flight_id, booking_reference,
                journey_date, passenger_names, seat_numbers, class_type,
                total_fare, booking_status)
Primary Key: booking_id
Foreign Key: user_id REFERENCES users(user_id)
Foreign Key: flight_id REFERENCES flights(flight_id)
```

**BOOKING_ACTIVITY_LOG (Trigger Table)**
```
booking_activity_log(log_id, booking_type, booking_reference, user_id,
                     action_type, old_status, new_status, total_fare,
                     journey_date, log_timestamp)
Primary Key: log_id
Foreign Key: user_id REFERENCES users(user_id)
```

### 5.2 Reference Tables

**KSRTC_ROUTES**
```
ksrtc_routes(route_id, route_name, origin, destination, distance_km,
             estimated_duration, base_fare)
Primary Key: route_id
```

**TRAINS**
```
trains(train_id, train_number, train_name, train_type, total_coaches)
Primary Key: train_id
Unique: train_number
```

**FLIGHTS**
```
flights(flight_id, airline_id, flight_number, origin_code, destination_code,
        aircraft_type)
Primary Key: flight_id
Foreign Key: airline_id REFERENCES airlines(airline_id)
```

---

## 6. DDL COMMANDS

### 6.1 Database Creation
```sql
DROP DATABASE IF EXISTS transport_system;
CREATE DATABASE transport_system 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE transport_system;
```

### 6.2 Users Table
```sql
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    user_type ENUM('user', 'admin') DEFAULT 'user',
    INDEX idx_email (email),
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 6.3 KSRTC Bookings Table
```sql
CREATE TABLE ksrtc_bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    schedule_id INT NOT NULL,
    booking_reference VARCHAR(50) UNIQUE NOT NULL,
    journey_date DATE NOT NULL,
    passenger_name VARCHAR(100) NOT NULL,
    passenger_age INT NOT NULL,
    passenger_gender ENUM('Male', 'Female', 'Other') NOT NULL,
    seat_numbers VARCHAR(100) NOT NULL,
    total_fare DECIMAL(10,2) NOT NULL,
    booking_status ENUM('Confirmed', 'Cancelled') DEFAULT 'Confirmed',
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (schedule_id) REFERENCES ksrtc_schedules(schedule_id),
    INDEX idx_user_bookings (user_id),
    INDEX idx_journey_date (journey_date),
    INDEX idx_booking_status (booking_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 6.4 Train Bookings Table
```sql
CREATE TABLE train_bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    train_id INT NOT NULL,
    pnr_number VARCHAR(10) UNIQUE NOT NULL,
    journey_date DATE NOT NULL,
    source_station VARCHAR(10) NOT NULL,
    destination_station VARCHAR(10) NOT NULL,
    coach_type VARCHAR(10) NOT NULL,
    seat_count INT NOT NULL,
    berth_preference VARCHAR(20),
    passenger_names TEXT NOT NULL,
    berth_numbers VARCHAR(200),
    total_fare DECIMAL(10,2) NOT NULL,
    booking_status ENUM('Confirmed', 'Cancelled', 'Waitlisted') DEFAULT 'Confirmed',
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (train_id) REFERENCES trains(train_id),
    INDEX idx_user_bookings (user_id),
    INDEX idx_pnr (pnr_number),
    INDEX idx_journey_date (journey_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 6.5 Flight Bookings Table
```sql
CREATE TABLE flight_bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    flight_id INT NOT NULL,
    booking_reference VARCHAR(50) UNIQUE NOT NULL,
    journey_date DATE NOT NULL,
    passenger_names TEXT NOT NULL,
    seat_numbers VARCHAR(200),
    class_type ENUM('Economy', 'Business', 'First') NOT NULL,
    total_fare DECIMAL(10,2) NOT NULL,
    booking_status ENUM('Confirmed', 'Cancelled') DEFAULT 'Confirmed',
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (flight_id) REFERENCES flights(flight_id),
    INDEX idx_user_bookings (user_id),
    INDEX idx_booking_ref (booking_reference),
    INDEX idx_journey_date (journey_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 6.6 Booking Activity Log (For Triggers)
```sql
CREATE TABLE booking_activity_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_type VARCHAR(20) NOT NULL,
    booking_reference VARCHAR(50) NOT NULL,
    user_id INT NOT NULL,
    action_type ENUM('INSERT', 'UPDATE') NOT NULL,
    old_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    total_fare DECIMAL(10,2) NOT NULL,
    journey_date DATE NOT NULL,
    log_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_booking_type (booking_type),
    INDEX idx_action_type (action_type),
    INDEX idx_log_timestamp (log_timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## 7. CRUD OPERATIONS - SCREENSHOTS REQUIRED

### 7.1 CREATE Operations
**Required Screenshots:**
1. ✅ **User Registration (Sign Up)**
   - Screenshot: `signup_page.png`
   - Capture: Form with username, email, password fields
   - Show: Successful registration message

2. ✅ **KSRTC Booking Creation**
   - Screenshot: `ksrtc_booking_form.png`
   - Capture: Seat selection interface with bus layout
   - Show: Booking confirmation with ticket details

3. ✅ **Train Booking Creation**
   - Screenshot: `train_booking_form.png`
   - Capture: Passenger details form with berth selection
   - Show: PNR number and booking confirmation

4. ✅ **Flight Booking Creation**
   - Screenshot: `flight_booking_form.png`
   - Capture: Seat selection and passenger details
   - Show: Booking reference and confirmation

### 7.2 READ Operations
**Required Screenshots:**
5. ✅ **User Login**
   - Screenshot: `signin_page.png`
   - Capture: Login form with username/password
   - Show: Session establishment

6. ✅ **View KSRTC Schedules**
   - Screenshot: `ksrtc_search_results.png`
   - Capture: List of available buses with details
   - Show: Bus type, timings, available seats, fare

7. ✅ **View Train Schedules**
   - Screenshot: `train_search_results.png`
   - Capture: Available trains between stations
   - Show: Train number, name, timings, available coaches

8. ✅ **View Flight Schedules**
   - Screenshot: `flight_search_results.png`
   - Capture: Flight listings with airline details
   - Show: Flight number, timings, available seats, fare

9. ✅ **View Booking History**
   - Screenshot: `user_booking_history.png`
   - Capture: User's past bookings (all modes)
   - Show: Booking details, status, download ticket option

10. ✅ **View Mobile Ticket**
    - Screenshot: `mobile_ticket_ksrtc.png`
    - Capture: Digital ticket with QR code
    - Show: Passenger details, journey info, booking reference

### 7.3 UPDATE Operations
**Required Screenshots:**
11. ✅ **Cancel KSRTC Booking**
    - Screenshot: `cancel_ksrtc_booking.png`
    - Capture: Booking details with cancel button
    - Show: Status changed to "Cancelled"

12. ✅ **Cancel Train Booking**
    - Screenshot: `cancel_train_booking.png`
    - Capture: PNR status before and after cancellation
    - Show: Refund details

13. ✅ **Cancel Flight Booking**
    - Screenshot: `cancel_flight_booking.png`
    - Capture: Booking reference with cancellation confirmation
    - Show: Updated status

### 7.4 DELETE Operations
14. ✅ **Account Deletion Flow**
    - Screenshot: `user_profile_delete.png`
    - Capture: Profile settings with delete account option
    - Show: Confirmation dialog and cascade deletion

---

## 8. FEATURES & FUNCTIONALITIES - SCREENSHOTS REQUIRED

### 8.1 User Dashboard
**Required Screenshots:**
15. ✅ **Main User Dashboard**
    - Screenshot: `user_dashboard.png`
    - Capture: Overview with booking statistics
    - Show: Total bookings, recent trips, quick actions

### 8.2 Admin Dashboard
**Required Screenshots:**
16. ✅ **Admin Analytics Dashboard**
    - Screenshot: `admin_dashboard_main.png`
    - Capture: Revenue charts and statistics
    - Show: Transport mode breakdown, booking trends

17. ✅ **Daily Revenue Breakdown**
    - Screenshot: `admin_daily_revenue.png`
    - Capture: Date picker with revenue cards
    - Show: KSRTC/Train/Flight revenue, top spenders table

18. ✅ **Peak Hours Chart**
    - Screenshot: `admin_peak_hours.png`
    - Capture: Bar chart showing hourly bookings
    - Show: Busiest hours for each transport mode

### 8.3 Expense Tracking
**Required Screenshots:**
19. ✅ **User Daily Expenses**
    - Screenshot: `user_daily_expenses.png`
    - Capture: Date selector with expense breakdown
    - Show: Gradient cards for KSRTC/Train/Flight expenses

20. ✅ **Monthly Expense Trends**
    - Screenshot: `user_monthly_expenses.png`
    - Capture: Line chart showing expense patterns
    - Show: Month-wise spending analysis

### 8.4 Live Tracking
**Required Screenshots:**
21. ✅ **KSRTC Live Bus Tracking**
    - Screenshot: `live_bus_tracking.png`
    - Capture: Map with bus location marker
    - Show: Real-time coordinates, route path, ETA

### 8.5 Search & Filter
**Required Screenshots:**
22. ✅ **Advanced KSRTC Search**
    - Screenshot: `ksrtc_search_page.png`
    - Capture: Route dropdown and date picker
    - Show: Filter options (bus type, departure time)

23. ✅ **Train Search with Stations**
    - Screenshot: `train_search_page.png`
    - Capture: Station code autocomplete
    - Show: Journey date and class selection

24. ✅ **Flight Search Interface**
    - Screenshot: `flight_search_page.png`
    - Capture: Airport code selection
    - Show: Date picker and class filter

### 8.6 Seat Selection
**Required Screenshots:**
25. ✅ **KSRTC Seat Layout**
    - Screenshot: `ksrtc_seat_selection.png`
    - Capture: Interactive bus seat map
    - Show: Available (green), booked (red), selected (blue) seats

26. ✅ **Flight Seat Map**
    - Screenshot: `flight_seat_selection.png`
    - Capture: Aircraft seating layout
    - Show: Class-wise seat distribution

### 8.7 Reports
**Required Screenshots:**
27. ✅ **Popular Routes Report**
    - Screenshot: `admin_popular_routes.png`
    - Capture: Table showing most booked routes
    - Show: Route name, booking count, revenue

28. ✅ **User Expense Summary**
    - Screenshot: `user_expense_report.png`
    - Capture: Comprehensive expense breakdown
    - Show: Transport mode wise totals, export option

---

## 9. TRIGGERS

### 9.1 KSRTC Booking Insert Trigger
```sql
DELIMITER //

CREATE TRIGGER after_ksrtc_booking_insert
AFTER INSERT ON ksrtc_bookings
FOR EACH ROW
BEGIN
    INSERT INTO booking_activity_log (
        booking_type, booking_reference, user_id, action_type,
        old_status, new_status, total_fare, journey_date
    ) VALUES (
        'KSRTC', NEW.booking_reference, NEW.user_id, 'INSERT',
        NULL, NEW.booking_status, NEW.total_fare, NEW.journey_date
    );
END//

DELIMITER ;
```

### 9.2 KSRTC Booking Update Trigger
```sql
DELIMITER //

CREATE TRIGGER after_ksrtc_booking_update
AFTER UPDATE ON ksrtc_bookings
FOR EACH ROW
BEGIN
    INSERT INTO booking_activity_log (
        booking_type, booking_reference, user_id, action_type,
        old_status, new_status, total_fare, journey_date
    ) VALUES (
        'KSRTC', NEW.booking_reference, NEW.user_id, 'UPDATE',
        OLD.booking_status, NEW.booking_status, NEW.total_fare, NEW.journey_date
    );
END//

DELIMITER ;
```

### 9.3 Train Booking Insert Trigger
```sql
DELIMITER //

CREATE TRIGGER after_train_booking_insert
AFTER INSERT ON train_bookings
FOR EACH ROW
BEGIN
    INSERT INTO booking_activity_log (
        booking_type, booking_reference, user_id, action_type,
        old_status, new_status, total_fare, journey_date
    ) VALUES (
        'Train', NEW.pnr_number, NEW.user_id, 'INSERT',
        NULL, NEW.booking_status, NEW.total_fare, NEW.journey_date
    );
END//

DELIMITER ;
```

### 9.4 Train Booking Update Trigger
```sql
DELIMITER //

CREATE TRIGGER after_train_booking_update
AFTER UPDATE ON train_bookings
FOR EACH ROW
BEGIN
    INSERT INTO booking_activity_log (
        booking_type, booking_reference, user_id, action_type,
        old_status, new_status, total_fare, journey_date
    ) VALUES (
        'Train', NEW.pnr_number, NEW.user_id, 'UPDATE',
        OLD.booking_status, NEW.booking_status, NEW.total_fare, NEW.journey_date
    );
END//

DELIMITER ;
```

### 9.5 Flight Booking Insert Trigger
```sql
DELIMITER //

CREATE TRIGGER after_flight_booking_insert
AFTER INSERT ON flight_bookings
FOR EACH ROW
BEGIN
    INSERT INTO booking_activity_log (
        booking_type, booking_reference, user_id, action_type,
        old_status, new_status, total_fare, journey_date
    ) VALUES (
        'Flight', NEW.booking_reference, NEW.user_id, 'INSERT',
        NULL, NEW.booking_status, NEW.total_fare, NEW.journey_date
    );
END//

DELIMITER ;
```

### 9.6 Flight Booking Update Trigger
```sql
DELIMITER //

CREATE TRIGGER after_flight_booking_update
AFTER UPDATE ON flight_bookings
FOR EACH ROW
BEGIN
    INSERT INTO booking_activity_log (
        booking_type, booking_reference, user_id, action_type,
        old_status, new_status, total_fare, journey_date
    ) VALUES (
        'Flight', NEW.booking_reference, NEW.user_id, 'UPDATE',
        OLD.booking_status, NEW.booking_status, NEW.total_fare, NEW.journey_date
    );
END//

DELIMITER ;
```

**Screenshot Required:**
29. ✅ **Trigger Execution Log**
    - Screenshot: `trigger_activity_log.png`
    - Capture: `SELECT * FROM booking_activity_log ORDER BY log_timestamp DESC LIMIT 20;`
    - Show: Log entries with booking_type, action_type, old/new status

---

## 10. PROCEDURES & FUNCTIONS

### 10.1 Stored Procedures (Code Snippets in Backend)

#### Procedure 1: Get User Booking Statistics
```python
# Backend API: /api/user/booking-stats
def get_user_booking_statistics(user_id):
    """Get comprehensive booking statistics for a user"""
    query = """
        SELECT 
            'KSRTC' as booking_type,
            COUNT(*) as total_bookings,
            SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END) as total_spent
        FROM ksrtc_bookings WHERE user_id = %s
        UNION ALL
        SELECT 
            'Train' as booking_type,
            COUNT(*) as total_bookings,
            SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END) as total_spent
        FROM train_bookings WHERE user_id = %s
        UNION ALL
        SELECT 
            'Flight' as booking_type,
            COUNT(*) as total_bookings,
            SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END) as total_spent
        FROM flight_bookings WHERE user_id = %s
    """
    return execute_query(query, (user_id, user_id, user_id), fetch=True)
```

#### Procedure 2: Get Daily Revenue (Admin)
```python
# Backend API: /api/admin/revenue/daily
def get_daily_revenue(date):
    """Calculate daily revenue across all transport modes"""
    query = """
        SELECT 
            'KSRTC' as mode,
            COUNT(*) as bookings,
            SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END) as revenue
        FROM ksrtc_bookings WHERE DATE(journey_date) = %s
        UNION ALL
        SELECT 
            'Train' as mode,
            COUNT(*) as bookings,
            SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END) as revenue
        FROM train_bookings WHERE DATE(journey_date) = %s
        UNION ALL
        SELECT 
            'Flight' as mode,
            COUNT(*) as bookings,
            SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END) as revenue
        FROM flight_bookings WHERE DATE(journey_date) = %s
    """
    return execute_query(query, (date, date, date), fetch=True)
```

#### Procedure 3: Get Top Spenders
```python
# Backend API: /api/admin/top-spenders
def get_top_spenders(date, limit=10):
    """Find top spending users on a given date"""
    query = """
        SELECT 
            u.user_id, u.username, u.email,
            SUM(revenue) as total_spent,
            SUM(bookings) as total_bookings
        FROM users u
        JOIN (
            SELECT user_id, 
                   SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END) as revenue,
                   COUNT(*) as bookings
            FROM ksrtc_bookings WHERE DATE(journey_date) = %s GROUP BY user_id
            UNION ALL
            SELECT user_id,
                   SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END) as revenue,
                   COUNT(*) as bookings
            FROM train_bookings WHERE DATE(journey_date) = %s GROUP BY user_id
            UNION ALL
            SELECT user_id,
                   SUM(CASE WHEN booking_status = 'Confirmed' THEN total_fare ELSE 0 END) as revenue,
                   COUNT(*) as bookings
            FROM flight_bookings WHERE DATE(journey_date) = %s GROUP BY user_id
        ) as booking_data ON u.user_id = booking_data.user_id
        GROUP BY u.user_id, u.username, u.email
        ORDER BY total_spent DESC
        LIMIT %s
    """
    return execute_query(query, (date, date, date, limit), fetch=True)
```

### 10.2 Code Invocation Screenshots Required

30. ✅ **Booking Statistics API Call**
    - Screenshot: `api_booking_stats.png`
    - Capture: Browser DevTools Network tab showing API response
    - Show: JSON response with booking counts and totals

31. ✅ **Daily Revenue Procedure Execution**
    - Screenshot: `api_daily_revenue.png`
    - Capture: API response in browser/Postman
    - Show: Revenue breakdown by transport mode

32. ✅ **Top Spenders Query Result**
    - Screenshot: `api_top_spenders.png`
    - Capture: Admin dashboard showing top spenders table
    - Show: User names, total spent, booking counts

---

## 11. ADVANCED SQL QUERIES

### 11.1 Nested Queries

#### Query 1: Find Users Who Spent More Than Average
```sql
SELECT u.username, u.email, 
       (SELECT SUM(total_fare) FROM ksrtc_bookings kb WHERE kb.user_id = u.user_id) +
       (SELECT SUM(total_fare) FROM train_bookings tb WHERE tb.user_id = u.user_id) +
       (SELECT SUM(total_fare) FROM flight_bookings fb WHERE fb.user_id = u.user_id) as total_expense
FROM users u
WHERE (
    (SELECT SUM(total_fare) FROM ksrtc_bookings kb WHERE kb.user_id = u.user_id) +
    (SELECT SUM(total_fare) FROM train_bookings tb WHERE tb.user_id = u.user_id) +
    (SELECT SUM(total_fare) FROM flight_bookings fb WHERE fb.user_id = u.user_id)
) > (
    SELECT AVG(total) FROM (
        SELECT SUM(total_fare) as total FROM ksrtc_bookings GROUP BY user_id
        UNION ALL
        SELECT SUM(total_fare) as total FROM train_bookings GROUP BY user_id
        UNION ALL
        SELECT SUM(total_fare) as total FROM flight_bookings GROUP BY user_id
    ) as avg_expenses
);
```

#### Query 2: Find Most Popular Route Per Transport Mode
```sql
SELECT booking_type, route, booking_count
FROM (
    SELECT 'KSRTC' as booking_type,
           CONCAT(source_station, ' to ', destination_station) as route,
           COUNT(*) as booking_count,
           ROW_NUMBER() OVER (PARTITION BY 'KSRTC' ORDER BY COUNT(*) DESC) as rn
    FROM ksrtc_bookings kb
    JOIN ksrtc_schedules s ON kb.schedule_id = s.schedule_id
    JOIN ksrtc_routes r ON s.route_id = r.route_id
    GROUP BY route
    
    UNION ALL
    
    SELECT 'Train' as booking_type,
           CONCAT(source_station, ' to ', destination_station) as route,
           COUNT(*) as booking_count,
           ROW_NUMBER() OVER (PARTITION BY 'Train' ORDER BY COUNT(*) DESC) as rn
    FROM train_bookings
    GROUP BY route
    
    UNION ALL
    
    SELECT 'Flight' as booking_type,
           CONCAT(origin_code, ' to ', destination_code) as route,
           COUNT(*) as booking_count,
           ROW_NUMBER() OVER (PARTITION BY 'Flight' ORDER BY COUNT(*) DESC) as rn
    FROM flight_bookings fb
    JOIN flights f ON fb.flight_id = f.flight_id
    GROUP BY route
) as ranked_routes
WHERE rn = 1;
```

**Screenshot Required:**
33. ✅ **Nested Query Results**
    - Screenshot: `nested_query_above_avg.png`
    - Capture: MySQL Workbench or terminal showing query execution
    - Show: Users with above-average expenses

### 11.2 Join Queries

#### Query 1: Get Complete Booking Details with User Info (KSRTC)
```sql
SELECT 
    u.username,
    u.email,
    kb.booking_reference,
    kb.journey_date,
    r.route_name,
    r.origin as source,
    r.destination,
    b.bus_number,
    b.bus_type,
    kb.seat_numbers,
    kb.total_fare,
    kb.booking_status
FROM users u
INNER JOIN ksrtc_bookings kb ON u.user_id = kb.user_id
INNER JOIN ksrtc_schedules s ON kb.schedule_id = s.schedule_id
INNER JOIN ksrtc_routes r ON s.route_id = r.route_id
INNER JOIN ksrtc_buses b ON s.bus_id = b.bus_id
WHERE kb.booking_status = 'Confirmed'
ORDER BY kb.booking_time DESC
LIMIT 50;
```

#### Query 2: Get Train Bookings with Complete Journey Info
```sql
SELECT 
    u.username,
    tb.pnr_number,
    t.train_number,
    t.train_name,
    tb.source_station,
    tb.destination_station,
    tb.journey_date,
    tb.coach_type,
    tb.seat_count,
    tb.total_fare,
    tb.booking_status
FROM users u
INNER JOIN train_bookings tb ON u.user_id = tb.user_id
INNER JOIN trains t ON tb.train_id = t.train_id
WHERE tb.journey_date >= CURDATE()
ORDER BY tb.journey_date, tb.booking_time;
```

#### Query 3: Get Flight Bookings with Airline and Airport Details
```sql
SELECT 
    u.username,
    fb.booking_reference,
    a.airline_name,
    f.flight_number,
    ap1.airport_name as origin_airport,
    ap1.city as origin_city,
    ap2.airport_name as destination_airport,
    ap2.city as destination_city,
    fb.journey_date,
    fb.class_type,
    fb.total_fare,
    fb.booking_status
FROM users u
INNER JOIN flight_bookings fb ON u.user_id = fb.user_id
INNER JOIN flights f ON fb.flight_id = f.flight_id
INNER JOIN airlines a ON f.airline_id = a.airline_id
INNER JOIN airports ap1 ON f.origin_code = ap1.airport_code
INNER JOIN airports ap2 ON f.destination_code = ap2.airport_code
WHERE fb.booking_status = 'Confirmed'
ORDER BY fb.journey_date;
```

**Screenshot Required:**
34. ✅ **Join Query Results - KSRTC**
    - Screenshot: `join_query_ksrtc.png`
    - Capture: Complete booking details with user and route info
    - Show: All joined columns clearly visible

35. ✅ **Join Query Results - Trains**
    - Screenshot: `join_query_trains.png`
    - Capture: Train bookings with journey details
    - Show: User, train, station information

36. ✅ **Join Query Results - Flights**
    - Screenshot: `join_query_flights.png`
    - Capture: Flight bookings with airline and airport names
    - Show: Complete journey information

### 11.3 Aggregate Queries

#### Query 1: Revenue Summary by Transport Mode
```sql
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
```

#### Query 2: Monthly Booking Trends
```sql
SELECT 
    DATE_FORMAT(journey_date, '%Y-%m') as month,
    COUNT(*) as total_bookings,
    SUM(total_fare) as monthly_revenue,
    AVG(total_fare) as avg_booking_value
FROM (
    SELECT journey_date, total_fare FROM ksrtc_bookings WHERE booking_status = 'Confirmed'
    UNION ALL
    SELECT journey_date, total_fare FROM train_bookings WHERE booking_status = 'Confirmed'
    UNION ALL
    SELECT journey_date, total_fare FROM flight_bookings WHERE booking_status = 'Confirmed'
) as all_bookings
GROUP BY month
ORDER BY month DESC
LIMIT 12;
```

#### Query 3: Peak Booking Hours Analysis
```sql
SELECT 
    HOUR(booking_time) as booking_hour,
    COUNT(*) as total_bookings,
    SUM(total_fare) as hourly_revenue,
    AVG(total_fare) as avg_booking_value
FROM (
    SELECT booking_time, total_fare FROM ksrtc_bookings
    UNION ALL
    SELECT booking_time, total_fare FROM train_bookings
    UNION ALL
    SELECT booking_time, total_fare FROM flight_bookings
) as all_bookings
GROUP BY booking_hour
ORDER BY total_bookings DESC;
```

**Screenshot Required:**
37. ✅ **Aggregate Query - Revenue Summary**
    - Screenshot: `aggregate_revenue_summary.png`
    - Capture: Transport mode wise statistics (COUNT, SUM, AVG, MAX, MIN)
    - Show: All aggregate functions clearly visible

38. ✅ **Aggregate Query - Monthly Trends**
    - Screenshot: `aggregate_monthly_trends.png`
    - Capture: Month-wise booking and revenue data
    - Show: GROUP BY results with calculated fields

39. ✅ **Aggregate Query - Peak Hours**
    - Screenshot: `aggregate_peak_hours.png`
    - Capture: Hour-wise booking distribution
    - Show: Peak hours highlighted

---

## 12. SQL FILES (.sql)

All SQL commands have been organized into the following files:

### Database Setup Files
1. **01_create_database.sql** - Database creation
2. **02_create_users_table.sql** - Users table with admin user
3. **03_create_routes_table.sql** - Routes for KSRTC, trains, flights
4. **04_create_transport_preferences.sql** - User preferences
5. **05_create_bookings_table.sql** - All booking tables
6. **06_create_live_tracking.sql** - GPS tracking table
7. **07_create_analytics_views.sql** - Analytics views
8. **08_triggers.sql** - All 6 triggers

### Sample Data Files
9. **insert_sample_ksrtc_data.sql** - KSRTC routes, buses, schedules
10. **insert_sample_train_data.sql** - Trains, stations, schedules
11. **insert_sample_flight_data.sql** - Airlines, airports, flights

### Query Files
12. **admin_analytics_queries.sql** - Revenue and analytics queries
13. **user_queries.sql** - User booking and expense queries
14. **aggregate_queries.sql** - All aggregate queries
15. **join_queries.sql** - Complex join examples
16. **nested_queries.sql** - Subquery examples

**Screenshot Required:**
40. ✅ **SQL Files Directory**
    - Screenshot: `sql_files_directory.png`
    - Capture: File explorer showing all .sql files
    - Show: File names and organization

---

## 13. GITHUB REPOSITORY

**Repository Link:** `[Your GitHub Repository URL]`

**Repository Structure:**
```
transport-system/
├── backend/
│   ├── app.py                    # Main Flask application
│   ├── config.py                 # Configuration settings
│   └── requirements.txt          # Python dependencies
├── frontend/
│   ├── index.html                # Landing page
│   ├── signin.html               # Login page
│   ├── signup.html               # Registration page
│   ├── ksrtc.html                # KSRTC booking page
│   ├── trains.html               # Train booking page
│   ├── flights.html              # Flight booking page
│   ├── expenses.html             # User expense tracking
│   ├── admin_dashboard.html      # Admin analytics
│   ├── mobile_tickets.html       # Digital tickets
│   ├── css/
│   │   └── styles.css            # Global styles
│   └── js/
│       ├── admin_dashboard.js    # Admin JS
│       ├── expenses.js           # Expense tracking JS
│       ├── ksrtc.js              # KSRTC booking JS
│       └── common.js             # Shared utilities
├── database/
│   ├── 01_create_database.sql
│   ├── 02_create_users_table.sql
│   ├── ...
│   └── 08_triggers.sql
├── docs/
│   ├── ER_DIAGRAM.png
│   ├── SCHEMA.png
│   └── PROJECT_REPORT.pdf
├── screenshots/
│   ├── crud/
│   ├── features/
│   ├── queries/
│   └── triggers/
├── README.md
└── requirements.txt
```

**Screenshot Required:**
41. ✅ **GitHub Repository Homepage**
    - Screenshot: `github_repo_homepage.png`
    - Capture: Repository main page with file structure
    - Show: Commit history, README preview

42. ✅ **GitHub Code Structure**
    - Screenshot: `github_code_structure.png`
    - Capture: Repository file tree expanded
    - Show: All directories and key files

---

## SUMMARY OF ALL REQUIRED SCREENSHOTS

### Total: 42 Screenshots Organized into Categories

#### **CRUD Operations (14 screenshots)**
1. signup_page.png
2. ksrtc_booking_form.png
3. train_booking_form.png
4. flight_booking_form.png
5. signin_page.png
6. ksrtc_search_results.png
7. train_search_results.png
8. flight_search_results.png
9. user_booking_history.png
10. mobile_ticket_ksrtc.png
11. cancel_ksrtc_booking.png
12. cancel_train_booking.png
13. cancel_flight_booking.png
14. user_profile_delete.png

#### **Features & Functionalities (14 screenshots)**
15. user_dashboard.png
16. admin_dashboard_main.png
17. admin_daily_revenue.png
18. admin_peak_hours.png
19. user_daily_expenses.png
20. user_monthly_expenses.png
21. live_bus_tracking.png
22. ksrtc_search_page.png
23. train_search_page.png
24. flight_search_page.png
25. ksrtc_seat_selection.png
26. flight_seat_selection.png
27. admin_popular_routes.png
28. user_expense_report.png

#### **Triggers & Procedures (5 screenshots)**
29. trigger_activity_log.png
30. api_booking_stats.png
31. api_daily_revenue.png
32. api_top_spenders.png
33. nested_query_above_avg.png

#### **Advanced Queries (6 screenshots)**
34. join_query_ksrtc.png
35. join_query_trains.png
36. join_query_flights.png
37. aggregate_revenue_summary.png
38. aggregate_monthly_trends.png
39. aggregate_peak_hours.png

#### **Repository & Files (3 screenshots)**
40. sql_files_directory.png
41. github_repo_homepage.png
42. github_code_structure.png

---

## ADDITIONAL DELIVERABLES CHECKLIST

### ✅ Completed Items
- [x] Cover Page with Team Details
- [x] Abstract (Section 1)
- [x] User Requirement Specification (Section 2)
- [x] Software/Tools List (Section 3)
- [x] ER Diagram (Section 4)
- [x] Relational Schema (Section 5)
- [x] DDL Commands (Section 6)
- [x] Triggers Definition (Section 9)
- [x] Procedures/Functions Code (Section 10)
- [x] Nested Queries (Section 11.1)
- [x] Join Queries (Section 11.2)
- [x] Aggregate Queries (Section 11.3)

### 📸 To Be Captured
- [ ] All 42 screenshots as listed above
- [ ] Organize screenshots into respective folders
- [ ] Label each screenshot clearly

### 📁 Files to Prepare
- [ ] Create separate .sql file for all CREATE statements
- [ ] Create separate .sql file for all INSERT statements
- [ ] Create separate .sql file for all Triggers
- [ ] Create separate .sql file for all Procedures/Functions
- [ ] Create separate .sql file for Nested queries
- [ ] Create separate .sql file for Join queries
- [ ] Create separate .sql file for Aggregate queries

### 🔗 Final Steps
- [ ] Upload all code to GitHub
- [ ] Add README.md with setup instructions
- [ ] Create release/tag for submission
- [ ] Update GitHub link in report
- [ ] Generate PDF of this report

---

## NOTES FOR SCREENSHOT CAPTURE

### Browser Setup
- Use latest Chrome/Firefox in full-screen mode
- Clear browser cache before capturing
- Use zoom level 100% for consistency
- Use incognito/private mode for clean UI

### Database Query Screenshots
- Use MySQL Workbench or command line
- Show full query and results
- Highlight important columns
- Include row counts

### API Screenshots
- Use Postman or Browser DevTools
- Show request URL and method
- Show response JSON clearly
- Include status codes

### UI Screenshots
- Capture full page with scrolling if needed
- Show meaningful data (not empty tables)
- Include timestamps where relevant
- Demonstrate actual functionality

---

**Document Version:** 1.0  
**Last Updated:** November 21, 2025  
**Prepared By:** [Team Name]  
**For:** DBMS Mini Project Submission
