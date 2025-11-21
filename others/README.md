# Multi-Modal Transport System

A comprehensive web application for multi-modal transportation planning and booking in Bangalore.

## Features

### User Features
- 🔐 User Authentication (Sign Up, Sign In)
- 🔍 Route Planning with multiple modes:
  - **Private Mode**: Bike, Car, Walk
  - **Public Mode**: BMTC, Metro, Aggregators
  - **Multi-Modal**: Combined transport with preferences for luggage, elderly, children, family
- 🎯 Route Optimization (Time, Cost, Fuel Efficiency)
- 📱 Booking Management (BMTC, Metro, Aggregators)
- 🚆 State Transport (KSRTC, Private Buses, Trains, Flights)
- 📦 Parcel Services
- ⏰ Live Tracking

### Admin Features
- 📊 Comprehensive Analytics Dashboard
- 📈 Transport Mode Usage Statistics
- 🗺️ Popular Routes Analysis
- 👥 User Activity Monitoring
- 💰 Booking Statistics
- 🔍 Preference Analysis (Private, Public, Multi-Modal)

## Technology Stack

### Backend
- Python 3.8+
- Flask (REST API)
- MySQL Database
- bcrypt (Password Hashing)
- JWT (Authentication)

### Frontend
- HTML5
- CSS3 (Responsive Design)
- JavaScript (ES6+)
- Mobile-Responsive UI

## Installation

### Prerequisites
- Python 3.8 or higher
- MySQL Server 8.0+
- Modern web browser

### Setup Instructions

1. **Install Python Dependencies**
```powershell
cd backend
pip install -r requirements.txt
```

2. **Configure Database**
   - Ensure MySQL is running on localhost
   - Update credentials in `backend/.env` if needed (default password: Darshu@2004)

3. **Setup Database**
```powershell
cd backend
python setup_database.py
```

4. **Start Backend Server**
```powershell
cd backend
python app.py
```

5. **Open Frontend**
   - Open `frontend/signin.html` in your browser
   - Or use a local server for better experience

## Default Credentials

### Admin Account
- **Username**: admin
- **Email**: admin@transport.com
- **Password**: Admin@123

## Project Structure

```
transport-system/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── database.py            # Database connection utilities
│   ├── setup_database.py      # Database setup script
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment configuration
├── database/
│   ├── 01_create_database.sql
│   ├── 02_create_users_table.sql
│   ├── 03_create_routes_table.sql
│   ├── 04_create_transport_preferences.sql
│   ├── 05_create_bookings_table.sql
│   ├── 06_create_live_tracking.sql
│   └── 07_create_analytics_views.sql
├── frontend/
│   ├── index.html             # Main user dashboard
│   ├── signin.html            # Sign in page
│   ├── signup.html            # Sign up page
│   ├── admin.html             # Admin dashboard
│   ├── css/
│   │   └── styles.css         # Global styles
│   └── js/
│       ├── auth.js            # Authentication logic
│       ├── app.js             # User app logic
│       └── admin.js           # Admin dashboard logic
└── README.md
```

## Database Schema

### Tables
- `users` - User accounts and authentication
- `route_searches` - Search history
- `transport_preferences` - User preferences per search
- `bookings` - All transport bookings
- `live_tracking` - Real-time tracking data

### Analytics Views
- `v_transport_mode_stats` - Mode usage statistics
- `v_popular_routes` - Most searched routes
- `v_private_mode_preferences` - Private transport preferences
- `v_public_mode_preferences` - Public transport preferences
- `v_multi_modal_distribution` - Multi-modal type distribution
- `v_booking_stats` - Booking statistics
- `v_user_activity` - User activity summary
- `v_optimization_preferences` - Route optimization preferences

## API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/signin` - User login

### Routes
- `POST /api/routes/search` - Search routes
- `GET /api/routes/history` - Get search history

### Bookings
- `POST /api/bookings/create` - Create booking
- `GET /api/bookings/my-bookings` - Get user bookings
- `GET /api/bookings/track/:id` - Track booking

### Admin (Protected)
- `GET /api/admin/dashboard` - Complete dashboard data
- `GET /api/admin/stats/transport-modes` - Transport mode stats
- `GET /api/admin/stats/popular-routes` - Popular routes
- `GET /api/admin/stats/private-mode` - Private mode stats
- `GET /api/admin/stats/public-mode` - Public mode stats
- `GET /api/admin/stats/multi-modal` - Multi-modal stats
- `GET /api/admin/stats/bookings` - Booking stats
- `GET /api/admin/stats/users` - User activity stats
- `GET /api/admin/stats/optimization` - Optimization preferences

## Mobile Responsiveness

The application is fully responsive and works on:
- 📱 Mobile devices (smartphones)
- 📱 Tablets
- 💻 Desktops
- 🖥️ Large screens

To access on mobile:
1. Ensure your phone is on the same network as your computer
2. Find your computer's local IP address
3. Open `http://YOUR_IP:5000` in your mobile browser
4. Open the frontend files through a local server

## Future Enhancements

- 🗺️ Real-time route mapping integration
- 🚌 Live BMTC bus tracking
- 🚇 Metro timings and status
- 💳 Payment gateway integration
- 📧 Email notifications
- 📱 Mobile app (iOS/Android)
- 🔔 Push notifications
- 🌐 Multi-language support

## License

This project is developed for educational and demonstration purposes.

## Support

For issues or questions, please contact the development team.
