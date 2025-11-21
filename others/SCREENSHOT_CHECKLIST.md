# SCREENSHOT CHECKLIST
## Multi-Modal Transport System - DBMS Mini Project

**Total Screenshots Required: 42**

---

## 📸 CATEGORY 1: CRUD OPERATIONS (14 Screenshots)

### CREATE Operations (4 screenshots)

#### ✅ Screenshot 1: User Registration
- **Filename:** `01_signup_page.png`
- **What to capture:**
  - Navigate to: `http://localhost:3000/signup.html`
  - Fill form with: username, email, password, full name, phone
  - Click "Sign Up" button
  - Capture: Full page with form filled + success message
- **Tips:** Use test data like username: "john_doe", email: "john@example.com"

#### ✅ Screenshot 2: KSRTC Booking
- **Filename:** `02_ksrtc_booking_form.png`
- **What to capture:**
  - Navigate to: `http://localhost:3000/ksrtc.html`
  - Search for buses, select schedule
  - Show seat selection interface (bus layout with colors)
  - Fill passenger details
  - Capture: Seat map + booking confirmation
- **Tips:** Select multiple seats to show selection feature

#### ✅ Screenshot 3: Train Booking
- **Filename:** `03_train_booking_form.png`
- **What to capture:**
  - Navigate to: `http://localhost:3000/trains.html`
  - Search trains by station codes
  - Select train and coach type
  - Fill passenger details with berth preference
  - Capture: Booking form + PNR confirmation
- **Tips:** Use station codes like SBC (Bangalore), MYS (Mysuru)

#### ✅ Screenshot 4: Flight Booking
- **Filename:** `04_flight_booking_form.png`
- **What to capture:**
  - Navigate to: `http://localhost:3000/flights.html`
  - Search flights by airport codes
  - Select flight and class
  - Choose seats from seat map
  - Capture: Seat selection + booking confirmation
- **Tips:** Use airport codes like BLR (Bangalore), DEL (Delhi)

---

### READ Operations (6 screenshots)

#### ✅ Screenshot 5: User Login
- **Filename:** `05_signin_page.png`
- **What to capture:**
  - Navigate to: `http://localhost:3000/signin.html`
  - Fill username/email and password
  - Show login button and form
  - Capture: Full login page before/after successful login
- **Tips:** Use credentials - admin/Admin@123 or your test user

#### ✅ Screenshot 6: KSRTC Search Results
- **Filename:** `06_ksrtc_search_results.png`
- **What to capture:**
  - Search for KSRTC buses
  - Show list of available buses with:
    - Bus number, type
    - Departure/arrival times
    - Available seats count
    - Fare amount
    - "Book Now" buttons
  - Capture: Full results page with multiple buses
- **Tips:** Search popular route like Bangalore to Mysuru

#### ✅ Screenshot 7: Train Search Results
- **Filename:** `07_train_search_results.png`
- **What to capture:**
  - Search for trains between stations
  - Show train list with:
    - Train number and name
    - Departure/arrival times
    - Available coaches (SL, 2A, 3A, etc.)
    - Fare for each class
  - Capture: Multiple train results
- **Tips:** Search SBC to MYS route

#### ✅ Screenshot 8: Flight Search Results
- **Filename:** `08_flight_search_results.png`
- **What to capture:**
  - Search for flights
  - Show flight list with:
    - Flight number, airline name
    - Origin and destination airports
    - Departure/arrival times
    - Available seats by class
    - Fare breakdown
  - Capture: Flight search results page
- **Tips:** Search BLR to DEL route

#### ✅ Screenshot 9: Booking History
- **Filename:** `09_user_booking_history.png`
- **What to capture:**
  - Navigate to user dashboard or bookings page
  - Show table with past bookings:
    - Booking reference/PNR
    - Transport mode (KSRTC/Train/Flight)
    - Journey details (route, date)
    - Status (Confirmed/Cancelled)
    - Download ticket button
  - Capture: Full booking history page
- **Tips:** Make 2-3 bookings first to populate history

#### ✅ Screenshot 10: Mobile Ticket
- **Filename:** `10_mobile_ticket_ksrtc.png`
- **What to capture:**
  - Navigate to: `http://localhost:3000/mobile_tickets.html`
  - Show digital ticket with:
    - QR code
    - Ticket number
    - Passenger details
    - Journey information (bus/train/flight details)
    - Booking reference
  - Capture: Full mobile ticket page
- **Tips:** Access from "View Ticket" in booking history

---

### UPDATE Operations (3 screenshots)

#### ✅ Screenshot 11: Cancel KSRTC Booking
- **Filename:** `11_cancel_ksrtc_booking.png`
- **What to capture:**
  - Show booking details page
  - Click "Cancel Booking" button
  - Show confirmation dialog
  - After cancellation: Status changed to "Cancelled"
  - Capture: Before and after cancellation (2 states)
- **Tips:** Create a test booking first, then cancel it

#### ✅ Screenshot 12: Cancel Train Booking
- **Filename:** `12_cancel_train_booking.png`
- **What to capture:**
  - Show train booking with PNR
  - Cancel button and confirmation
  - Status update to "Cancelled"
  - Refund information (if displayed)
  - Capture: Booking details showing cancellation
- **Tips:** Cancel a confirmed train booking

#### ✅ Screenshot 13: Cancel Flight Booking
- **Filename:** `13_cancel_flight_booking.png`
- **What to capture:**
  - Show flight booking reference
  - Cancellation process
  - Updated status
  - Capture: Flight booking showing cancelled status
- **Tips:** Use a test flight booking

---

### DELETE Operations (1 screenshot)

#### ✅ Screenshot 14: Account Deletion
- **Filename:** `14_user_profile_delete.png`
- **What to capture:**
  - User profile/settings page
  - "Delete Account" option
  - Confirmation dialog warning
  - Capture: Profile page with delete option
- **Tips:** DON'T actually delete your test account! Just show the option

---

## 📊 CATEGORY 2: FEATURES & FUNCTIONALITIES (14 Screenshots)

### Dashboards (3 screenshots)

#### ✅ Screenshot 15: User Dashboard
- **Filename:** `15_user_dashboard.png`
- **What to capture:**
  - Navigate to user homepage after login
  - Show statistics cards:
    - Total bookings
    - Recent trips
    - Upcoming journeys
  - Quick action buttons
  - Capture: Full dashboard view
- **Tips:** Login as regular user (not admin)

#### ✅ Screenshot 16: Admin Main Dashboard
- **Filename:** `16_admin_dashboard_main.png`
- **What to capture:**
  - Navigate to: `http://localhost:3000/admin_dashboard.html`
  - Login as admin (admin/Admin@123)
  - Show analytics cards:
    - Total revenue
    - Transport mode breakdown charts
    - Booking trends graph
  - Capture: Full admin dashboard with charts
- **Tips:** Ensure Chart.js graphs are visible

#### ✅ Screenshot 17: Admin Daily Revenue
- **Filename:** `17_admin_daily_revenue.png`
- **What to capture:**
  - Scroll to "Daily Revenue Breakdown" section
  - Select a date with bookings
  - Show 4 gradient cards:
    - Total Revenue
    - KSRTC Revenue
    - Train Revenue
    - Flight Revenue
  - Show "Top Spenders Today" table below cards
  - Capture: Revenue cards + top spenders table
- **Tips:** Choose today's date or a date with bookings

#### ✅ Screenshot 18: Peak Hours Chart
- **Filename:** `18_admin_peak_hours.png`
- **What to capture:**
  - Find "Peak Booking Hours" section on admin dashboard
  - Show bar chart with hourly bookings
  - X-axis: Hours (00:00 to 23:00)
  - Y-axis: Number of bookings
  - Different colors for KSRTC, Train, Flight
  - Capture: Complete chart with legend
- **Tips:** Make bookings at different times to populate chart

---

### Expense Tracking (2 screenshots)

#### ✅ Screenshot 19: User Daily Expenses
- **Filename:** `19_user_daily_expenses.png`
- **What to capture:**
  - Navigate to: `http://localhost:3000/expenses.html`
  - Select a date with bookings
  - Show gradient cards:
    - Total Daily Expenses
    - KSRTC Expenses
    - Train Expenses
    - Flight Expenses
  - Show "Recent Bookings" table
  - Capture: Expense cards + bookings table
- **Tips:** Login as user who made bookings

#### ✅ Screenshot 20: Monthly Expense Trends
- **Filename:** `20_user_monthly_expenses.png`
- **What to capture:**
  - Find monthly expense chart on expenses page
  - Show line/bar chart with month-wise spending
  - X-axis: Months
  - Y-axis: Amount spent
  - Legend showing transport modes
  - Capture: Monthly trends chart
- **Tips:** Make bookings across different months

---

### Live Tracking (1 screenshot)

#### ✅ Screenshot 21: KSRTC Live Tracking
- **Filename:** `21_live_bus_tracking.png`
- **What to capture:**
  - Navigate to live tracking page (if available)
  - Show map with bus location marker
  - Display:
    - Bus number
    - Route information
    - Current location coordinates
    - ETA to destination
  - Capture: Map view with tracking info
- **Tips:** May need to have active KSRTC booking

---

### Search & Filter (3 screenshots)

#### ✅ Screenshot 22: KSRTC Search Page
- **Filename:** `22_ksrtc_search_page.png`
- **What to capture:**
  - KSRTC homepage with search form
  - Show route dropdown (origin/destination)
  - Date picker
  - Filter options (bus type, departure time)
  - Search button
  - Capture: Clean search interface
- **Tips:** Don't click search yet - just show the form

#### ✅ Screenshot 23: Train Search Page
- **Filename:** `23_train_search_page.png`
- **What to capture:**
  - Train search form
  - Station code inputs with autocomplete
  - Journey date selector
  - Class filter (SL, 2A, 3A, etc.)
  - Capture: Search form with all fields
- **Tips:** Show autocomplete dropdown if possible

#### ✅ Screenshot 24: Flight Search Page
- **Filename:** `24_flight_search_page.png`
- **What to capture:**
  - Flight search interface
  - Airport code selection dropdowns
  - Date picker
  - Class filter (Economy, Business, First)
  - Passenger count
  - Capture: Complete search form
- **Tips:** Show airport dropdown with city names

---

### Seat Selection (2 screenshots)

#### ✅ Screenshot 25: KSRTC Seat Layout
- **Filename:** `25_ksrtc_seat_selection.png`
- **What to capture:**
  - Interactive bus seat map
  - Color coding:
    - Green: Available seats
    - Red: Already booked
    - Blue: Currently selected by you
  - Seat numbers visible
  - Legend explaining colors
  - Capture: Full seat layout with some seats selected
- **Tips:** Select 2-3 seats to show selection feature

#### ✅ Screenshot 26: Flight Seat Map
- **Filename:** `26_flight_seat_selection.png`
- **What to capture:**
  - Aircraft seating layout
  - Different sections (Economy, Business, First)
  - Seat availability colors
  - Row and column labels (1A, 1B, etc.)
  - Capture: Flight seat map with selections
- **Tips:** Show different class sections clearly

---

### Reports (2 screenshots)

#### ✅ Screenshot 27: Popular Routes Report
- **Filename:** `27_admin_popular_routes.png`
- **What to capture:**
  - Admin dashboard section showing popular routes
  - Table with columns:
    - Route name
    - Booking count
    - Total revenue
  - Sorted by popularity
  - Capture: Routes table on admin page
- **Tips:** Find analytics section on admin dashboard

#### ✅ Screenshot 28: User Expense Report
- **Filename:** `28_user_expense_report.png`
- **What to capture:**
  - Expense summary page
  - Breakdown by transport mode
  - Total amounts
  - Export/download option (if available)
  - Capture: Complete expense report
- **Tips:** User expense page with summary table

---

## 🔧 CATEGORY 3: TRIGGERS & PROCEDURES (5 Screenshots)

#### ✅ Screenshot 29: Trigger Activity Log
- **Filename:** `29_trigger_activity_log.png`
- **What to capture:**
  - Open MySQL Workbench or terminal
  - Run query:
    ```sql
    SELECT * FROM booking_activity_log 
    ORDER BY log_timestamp DESC 
    LIMIT 20;
    ```
  - Show table with columns:
    - booking_type, booking_reference
    - action_type (INSERT/UPDATE)
    - old_status, new_status
    - total_fare, log_timestamp
  - Capture: Query + results table
- **Tips:** Make a booking first to populate log

#### ✅ Screenshot 30: Booking Statistics API
- **Filename:** `30_api_booking_stats.png`
- **What to capture:**
  - Open browser DevTools (F12)
  - Go to Network tab
  - Trigger API call from admin dashboard
  - Show API endpoint: `/api/admin/booking-stats`
  - Display JSON response with booking counts
  - Capture: Network tab with request/response
- **Tips:** Use Chrome/Firefox DevTools

#### ✅ Screenshot 31: Daily Revenue API
- **Filename:** `31_api_daily_revenue.png`
- **What to capture:**
  - DevTools Network tab
  - API call: `/api/admin/revenue/daily?date=2025-11-21`
  - Show JSON response:
    ```json
    {
      "ksrtc_revenue": 1500,
      "train_revenue": 2300,
      "flight_revenue": 19500
    }
    ```
  - Capture: Request URL + JSON response
- **Tips:** Use date with actual bookings

#### ✅ Screenshot 32: Top Spenders API
- **Filename:** `32_api_top_spenders.png`
- **What to capture:**
  - API endpoint: `/api/admin/top-spenders`
  - JSON response showing users array:
    - username, email
    - total_spent, booking_count
  - Capture: Network tab with response data
- **Tips:** Load admin dashboard to trigger API

#### ✅ Screenshot 33: Nested Query Results
- **Filename:** `33_nested_query_above_avg.png`
- **What to capture:**
  - MySQL Workbench or terminal
  - Run nested query from `nested_queries.sql`:
    ```sql
    -- Query 1: Users who spent more than average
    ```
  - Show results with usernames and total_expense
  - Capture: Full query + results table
- **Tips:** Ensure query executes successfully

---

## 📑 CATEGORY 4: ADVANCED QUERIES (6 Screenshots)

### Join Queries (3 screenshots)

#### ✅ Screenshot 34: Join Query - KSRTC
- **Filename:** `34_join_query_ksrtc.png`
- **What to capture:**
  - Run query from `join_queries.sql` (Query 1)
  - Shows users + bookings + schedules + routes + buses
  - Result columns:
    - username, email, booking_reference
    - route_name, bus_number, total_fare
  - Capture: Query text + results table
- **Tips:** Scroll to show all columns

#### ✅ Screenshot 35: Join Query - Trains
- **Filename:** `35_join_query_trains.png`
- **What to capture:**
  - Run query from `join_queries.sql` (Query 2)
  - Join: users + train_bookings + trains + stations
  - Show columns:
    - PNR, train_name
    - source/destination stations with city names
  - Capture: Query + results
- **Tips:** Ensure station names are visible

#### ✅ Screenshot 36: Join Query - Flights
- **Filename:** `36_join_query_flights.png`
- **What to capture:**
  - Run query from `join_queries.sql` (Query 3)
  - Join: users + flight_bookings + flights + airlines + airports
  - Show:
    - airline_name, flight_number
    - origin/destination airport names and cities
  - Capture: Complete query results
- **Tips:** Show airport city names clearly

---

### Aggregate Queries (3 screenshots)

#### ✅ Screenshot 37: Revenue Summary (Aggregates)
- **Filename:** `37_aggregate_revenue_summary.png`
- **What to capture:**
  - Run query from `aggregate_queries.sql` (Query 1)
  - Shows transport_mode with:
    - COUNT(*) - total bookings
    - SUM(total_fare) - revenue
    - AVG(total_fare) - average fare
    - MAX/MIN fares
  - Capture: Query + aggregate results
- **Tips:** Highlight aggregate functions in query

#### ✅ Screenshot 38: Monthly Trends (GROUP BY)
- **Filename:** `38_aggregate_monthly_trends.png`
- **What to capture:**
  - Run query from `aggregate_queries.sql` (Query 2)
  - Monthly aggregation with GROUP BY
  - Show:
    - Month, total_bookings
    - monthly_revenue
    - avg_booking_value
  - Capture: Query with GROUP BY + results
- **Tips:** Show at least 3-6 months of data

#### ✅ Screenshot 39: Peak Hours Analysis
- **Filename:** `39_aggregate_peak_hours.png`
- **What to capture:**
  - Run query from `aggregate_queries.sql` (Query 3)
  - Hourly aggregation using HOUR() function
  - Show:
    - booking_hour (0-23)
    - total_bookings per hour
    - hourly_revenue
  - Capture: Query + hourly breakdown
- **Tips:** Make bookings at different times

---

## 📦 CATEGORY 5: REPOSITORY & FILES (3 Screenshots)

#### ✅ Screenshot 40: SQL Files Directory
- **Filename:** `40_sql_files_directory.png`
- **What to capture:**
  - File Explorer window
  - Navigate to: `New folder (4)/sql_files/`
  - Show all .sql files:
    - complete_ddl_commands.sql
    - aggregate_queries.sql
    - join_queries.sql
    - nested_queries.sql
  - Show file sizes and dates
  - Capture: Full directory view
- **Tips:** List view shows more info than icons

#### ✅ Screenshot 41: GitHub Repository Homepage
- **Filename:** `41_github_repo_homepage.png`
- **What to capture:**
  - GitHub repository main page
  - Show:
    - Repository name and description
    - Commit count and branches
    - README.md preview
    - File/folder structure
  - Capture: Full GitHub homepage
- **Tips:** Create repo first and push all code

#### ✅ Screenshot 42: GitHub Code Structure
- **Filename:** `42_github_code_structure.png`
- **What to capture:**
  - GitHub repository file tree
  - Expand folders to show:
    - backend/ (app.py)
    - frontend/ (HTML files)
    - database/ (SQL files)
    - sql_files/ (query files)
  - Capture: Expanded directory tree
- **Tips:** Click on folders to expand them

---

## 📝 SCREENSHOT CAPTURE TIPS

### General Guidelines
1. **Resolution:** Use 1920x1080 or higher
2. **Format:** Save as PNG (better quality than JPG)
3. **Browser:** Use Chrome/Firefox with clean UI (no bookmark bar clutter)
4. **Zoom:** Keep browser zoom at 100%
5. **DevTools:** Close when not needed for cleaner screenshots

### Tool Recommendations
- **Windows:** Win + Shift + S (Snipping Tool)
- **Greenshot:** Free screenshot tool with annotation
- **ShareX:** Advanced screenshot with auto-naming
- **Lightshot:** Quick screenshots with upload

### Naming Convention
- Use numbers: `01_`, `02_`, etc.
- Use underscores for spaces
- Be descriptive: `15_user_dashboard.png`
- Keep lowercase

### Organization
Create folders:
```
screenshots/
├── 01_crud/          (Screenshots 1-14)
├── 02_features/      (Screenshots 15-28)
├── 03_triggers/      (Screenshots 29-33)
├── 04_queries/       (Screenshots 34-39)
└── 05_repo/          (Screenshots 40-42)
```

### Quality Checklist
- ✅ Full page visible (no cropping important parts)
- ✅ Clear text (readable font sizes)
- ✅ No personal information visible (if sensitive)
- ✅ Data populated (not empty tables)
- ✅ Proper lighting (bright, clear colors)
- ✅ No browser errors in console (F12)

---

## 🎯 QUICK CAPTURE ORDER

**Suggested order for efficiency:**

### Session 1: Setup & CRUD (1-14)
1. Start both servers (backend + frontend)
2. Create test user account (Screenshot 1)
3. Login as user (Screenshot 5)
4. Make KSRTC booking (Screenshots 2, 6, 22, 25)
5. Make Train booking (Screenshots 3, 7, 23)
6. Make Flight booking (Screenshots 4, 8, 24, 26)
7. View booking history (Screenshot 9)
8. View mobile ticket (Screenshot 10)
9. Cancel bookings (Screenshots 11-13)
10. Show profile page (Screenshot 14)

### Session 2: Admin Features (15-18, 27-32)
1. Login as admin
2. Admin dashboard (Screenshot 16)
3. Daily revenue (Screenshot 17)
4. Peak hours chart (Screenshot 18)
5. Popular routes (Screenshot 27)
6. Open DevTools for API calls (Screenshots 30-32)

### Session 3: User Features (19-21, 28)
1. Login as regular user
2. User dashboard (Screenshot 15)
3. Daily expenses (Screenshot 19)
4. Monthly expenses (Screenshot 20)
5. Expense report (Screenshot 28)
6. Live tracking (Screenshot 21)

### Session 4: Database Queries (29, 33-39)
1. Open MySQL Workbench
2. Run trigger log query (Screenshot 29)
3. Execute nested queries (Screenshot 33)
4. Run join queries (Screenshots 34-36)
5. Execute aggregate queries (Screenshots 37-39)

### Session 5: Files & GitHub (40-42)
1. Screenshot SQL files folder (Screenshot 40)
2. Create GitHub repository
3. Push all code
4. Screenshot GitHub homepage (Screenshot 41)
5. Screenshot file structure (Screenshot 42)

---

## ✅ FINAL CHECKLIST

Before submitting:
- [ ] All 42 screenshots captured
- [ ] Filenames match specification
- [ ] Screenshots organized in folders
- [ ] Clear, readable quality
- [ ] No error messages visible (unless intentional)
- [ ] Data populated in all tables/charts
- [ ] GitHub repo link updated in PROJECT_REPORT.md
- [ ] All SQL files created and tested
- [ ] README.md complete with setup instructions

---

**Good luck with your screenshots!** 📸
