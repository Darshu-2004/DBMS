# 🚍🚂✈️ Multi-Modal Transport System
## DBMS Mini Project - Database Management System

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.0-green.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive web-based transport booking system integrating multiple modes of transportation (KSRTC buses, trains, and flights) with real-time tracking, analytics, and expense management.

---

## 📋 Table of Contents
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Database Setup](#-database-setup)
- [Running the Application](#-running-the-application)
- [Screenshots](#-screenshots)
- [Database Design](#-database-design)
- [API Endpoints](#-api-endpoints)
- [Contributing](#-contributing)
- [Team](#-team)

---

## ✨ Features

### For Users
- 🎫 **Multi-Modal Booking**: Book KSRTC buses, trains, and flights from one platform
- 💺 **Interactive Seat Selection**: Visual seat maps for buses and flights
- 📱 **Digital Tickets**: Download mobile tickets with QR codes
- 📊 **Expense Tracking**: Track daily and monthly travel expenses
- 🗺️ **Live Tracking**: Real-time GPS tracking for KSRTC buses
- 📜 **Booking History**: View and manage all past bookings
- ❌ **Easy Cancellations**: Cancel bookings with one click

### For Administrators
- 📈 **Revenue Analytics**: Daily, monthly, and yearly revenue breakdowns
- 👥 **User Analytics**: Top spenders, user activity, and behavior analysis
- ⏰ **Peak Hours Analysis**: Identify busiest booking times
- 🛤️ **Popular Routes**: Track most frequently booked routes
- 📊 **Real-time Dashboard**: Live statistics and charts
- 💳 **Payment Tracking**: Monitor all transactions

---

## 🛠 Tech Stack

### Backend
- **Framework**: Flask (Python 3.10+)
- **Database**: MySQL 8.0
- **Spatial Database**: PostGIS (for GPS tracking)
- **Authentication**: bcrypt password hashing
- **API**: RESTful API architecture

### Frontend
- **HTML5** with semantic markup
- **CSS3** with gradients and animations
- **JavaScript (ES6+)** for dynamic interactions
- **Chart.js** for data visualization
- **Responsive Design** for mobile compatibility

### Database Features
- **Triggers**: 6 AFTER INSERT/UPDATE triggers for activity logging
- **Views**: Multiple analytical views for reporting
- **Stored Procedures**: Backend API functions for complex queries
- **Indexes**: Optimized for fast search and retrieval

---

## 📁 Project Structure

```
DBMS/
├── backend/
│   ├── app.py                          # Main Flask application
│   ├── config.py                       # Configuration settings
│   └── requirements.txt                # Python dependencies
│
├── frontend/
│   ├── index.html                      # Landing page
│   ├── signin.html                     # User login
│   ├── signup.html                     # User registration
│   ├── ksrtc.html                      # KSRTC booking
│   ├── trains.html                     # Train booking
│   ├── flights.html                    # Flight booking
│   ├── expenses.html                   # Expense tracking
│   ├── admin_dashboard.html            # Admin analytics
│   ├── mobile_tickets.html             # Digital tickets
│   ├── css/
│   │   └── styles.css                  # Global styles
│   └── js/
│       ├── admin_dashboard.js          # Admin JS
│       ├── expenses.js                 # Expense tracking
│       └── common.js                   # Shared utilities
│
├── database/
│   ├── 01_create_database.sql          # Database creation
│   ├── 02_create_users_table.sql       # Users table
│   ├── 03_create_routes_table.sql      # Routes for all modes
│   ├── 04_create_transport_preferences.sql
│   ├── 05_create_bookings_table.sql    # Booking tables
│   ├── 06_create_live_tracking.sql     # GPS tracking
│   ├── 07_create_analytics_views.sql   # Analytical views
│   └── 08_triggers.sql                 # All triggers
│
├── sql_files/
│   ├── complete_ddl_commands.sql       # All CREATE statements
│   ├── aggregate_queries.sql           # SUM, COUNT, AVG queries
│   ├── join_queries.sql                # INNER/LEFT JOIN queries
│   └── nested_queries.sql              # Subquery examples
│
├── docs/
│   ├── PROJECT_REPORT.md               # Complete project documentation
│   ├── SCREENSHOT_CHECKLIST.md         # Screenshot guide
│   ├── DELIVERABLES_SUMMARY.md         # Project status
│   └── QUICK_SCREENSHOT_GUIDE.md       # Quick reference
│
├── .gitignore
└── README.md
```

---

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- MySQL 8.0 or higher
- PostgreSQL with PostGIS (for live tracking)
- Git

### Step 1: Clone Repository
```bash
git clone https://github.com/Darshu-2004/DBMS.git
cd DBMS
```

### Step 2: Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

**Required packages:**
- Flask==2.3.0
- Flask-CORS==4.0.0
- mysql-connector-python==8.0.33
- bcrypt==4.0.1
- psycopg2-binary==2.9.6
- python-dotenv==1.0.0

### Step 3: Configure Database
Create a `.env` file in the `backend/` directory:
```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=transport_system

POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DATABASE=transport_gis
```

---

## 💾 Database Setup

### Step 1: Create MySQL Database
```bash
mysql -u root -p < database/01_create_database.sql
mysql -u root -p < database/02_create_users_table.sql
mysql -u root -p < database/03_create_routes_table.sql
mysql -u root -p < database/04_create_transport_preferences.sql
mysql -u root -p < database/05_create_bookings_table.sql
mysql -u root -p < database/06_create_live_tracking.sql
mysql -u root -p < database/07_create_analytics_views.sql
mysql -u root -p < database/08_triggers.sql
```

Or run all at once:
```bash
cd database
for file in *.sql; do mysql -u root -p transport_system < "$file"; done
```

### Step 2: Insert Sample Data (Optional)
```bash
mysql -u root -p transport_system < database/insert_sample_data.sql
```

### Step 3: Verify Installation
```bash
mysql -u root -p -e "USE transport_system; SHOW TABLES;"
```

Expected output: 34+ tables including bookings, users, routes, etc.

---

## ▶️ Running the Application

### Start Backend Server
```bash
cd backend
python app.py
```
Backend will run on: `http://localhost:5000`

### Start Frontend Server
Open a new terminal:
```bash
cd frontend
python -m http.server 3000
```
Frontend will run on: `http://localhost:3000`

### Access the Application
1. **User Interface**: http://localhost:3000/index.html
2. **Admin Dashboard**: http://localhost:3000/admin_dashboard.html

### Default Credentials
| Role | Username | Password |
|------|----------|----------|
| Admin | admin | Admin@123 |
| User | (register new user) | - |

---

## 📸 Screenshots

### User Interface
![Landing Page](docs/screenshots/01_landing_page.png)
*Modern landing page with transport mode options*

![KSRTC Booking](docs/screenshots/02_ksrtc_booking.png)
*Interactive seat selection for KSRTC buses*

![Train Search](docs/screenshots/03_train_search.png)
*Train search with station autocomplete*

### Admin Dashboard
![Admin Analytics](docs/screenshots/04_admin_dashboard.png)
*Real-time revenue and booking analytics*

![Revenue Breakdown](docs/screenshots/05_revenue_breakdown.png)
*Daily revenue breakdown by transport mode*

---

## 🗄️ Database Design

### ER Diagram
```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│    USERS    │         │   BOOKINGS   │         │   ROUTES    │
├─────────────┤         ├──────────────┤         ├─────────────┤
│ user_id (PK)│◄────────┤ booking_id(PK)│         │ route_id(PK)│
│ username    │         │ user_id (FK) │         │ source      │
│ email       │         │ booking_type │         │ destination │
│ password    │         │ journey_date │         │ distance    │
└─────────────┘         └──────────────┘         └─────────────┘
```

### Key Tables
- **users**: User accounts and authentication
- **ksrtc_bookings**: KSRTC bus bookings
- **train_bookings**: Railway reservations
- **flight_bookings**: Flight bookings
- **booking_activity_log**: Trigger-based activity tracking

### Database Triggers
6 triggers automatically log all booking activities:
- `after_ksrtc_booking_insert` / `after_ksrtc_booking_update`
- `after_train_booking_insert` / `after_train_booking_update`
- `after_flight_booking_insert` / `after_flight_booking_update`

---

## 🔌 API Endpoints

### User APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/user/register` | Register new user |
| POST | `/api/user/login` | User authentication |
| GET | `/api/user/bookings` | Get user bookings |
| GET | `/api/user/expenses/daily` | Daily expense breakdown |
| POST | `/api/ksrtc/book` | Book KSRTC bus |
| POST | `/api/train/book` | Book train ticket |
| POST | `/api/flight/book` | Book flight ticket |

### Admin APIs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/revenue/daily` | Daily revenue stats |
| GET | `/api/admin/top-spenders` | Top spending users |
| GET | `/api/admin/popular-routes` | Most booked routes |
| GET | `/api/admin/peak-hours` | Peak booking hours |

---

## 🎯 Key Features Implementation

### 1. Advanced SQL Queries
- **Aggregate Queries**: Revenue summaries with SUM, AVG, COUNT
- **Join Queries**: 4-6 table joins for comprehensive data
- **Nested Queries**: Subqueries for complex filtering
- **Window Functions**: ROW_NUMBER for ranking

### 2. Database Triggers
All bookings are automatically logged for audit trail:
```sql
CREATE TRIGGER after_ksrtc_booking_insert
AFTER INSERT ON ksrtc_bookings
FOR EACH ROW
BEGIN
    INSERT INTO booking_activity_log (...)
    VALUES (...);
END;
```

### 3. Real-Time Features
- Live seat availability checking
- Dynamic fare calculation
- Instant booking confirmation
- Real-time GPS tracking (PostGIS)

### 4. Security
- bcrypt password hashing
- SQL injection prevention (parameterized queries)
- XSS protection
- Session-based authentication

---

## 📊 Analytics & Reporting

### Available Reports
1. **Revenue Reports**
   - Daily/Monthly/Yearly revenue
   - Transport mode-wise breakdown
   - Top revenue-generating routes

2. **User Reports**
   - User expense summaries
   - Booking frequency analysis
   - Multi-modal usage patterns

3. **Operational Reports**
   - Peak booking hours
   - Cancellation statistics
   - Seat occupancy rates

---

## 🧪 Testing

### Run Test Suite
```bash
cd backend
python -m pytest tests/
```

### Manual Testing Checklist
- [ ] User registration and login
- [ ] KSRTC booking (search, select, book)
- [ ] Train booking (PNR generation)
- [ ] Flight booking (seat selection)
- [ ] Booking cancellation
- [ ] Expense tracking
- [ ] Admin dashboard loading
- [ ] Daily revenue calculation
- [ ] Trigger execution

---

## 📚 Documentation

Complete project documentation available in `/docs`:
- **PROJECT_REPORT.md**: Comprehensive project report
- **SCREENSHOT_CHECKLIST.md**: UI screenshot guide
- **DELIVERABLES_SUMMARY.md**: Project deliverables
- **SQL Query Files**: All database queries organized by type

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 👥 Team

**Project Team:**
- DARSHITH M S 
- BANASHANKAR



**Course:** Database Management Systems (UE23CS351A)  
**Academic Year:** 2024-25

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Flask documentation and community
- MySQL documentation
- Chart.js for visualization library
- OpenStreetMap for GPS data
- All contributors and testers

---

## 📧 Contact

For questions or support:
- **GitHub Issues**: [Create an issue](https://github.com/Darshu-2004/DBMS/issues)
- **Email**: [your-email@example.com]

---

## 🔗 Links

- **Live Demo**: [Coming Soon]
- **Documentation**: [/docs](./docs)
- **Project Report**: [PROJECT_REPORT.md](./PROJECT_REPORT.md)
- **SQL Files**: [/sql_files](./sql_files)

---

**⭐ If you found this project useful, please consider giving it a star!**

---

*Last Updated: November 22, 2025*
