# 📸 SCREENSHOT QUICK REFERENCE
## Fast Guide to Capture All 42 Screenshots

---

## 🚀 BEFORE YOU START

### Setup Checklist
- [ ] Backend running: `python backend/app.py` (Port 5000)
- [ ] Frontend running: `python -m http.server 3000` (Port 3000)
- [ ] MySQL database populated with sample data
- [ ] Browser at 100% zoom, clear cache
- [ ] Screenshot tool ready (Win+Shift+S or Greenshot)
- [ ] Create folder: `screenshots/` with subfolders

---

## 📝 QUICK CAPTURE LIST

### 🔵 CRUD - CREATE (4 shots)
| # | File | URL | Action |
|---|------|-----|--------|
| 1 | `01_signup_page.png` | `/signup.html` | Fill form + register |
| 2 | `02_ksrtc_booking_form.png` | `/ksrtc.html` | Select seats + book |
| 3 | `03_train_booking_form.png` | `/trains.html` | Book train + show PNR |
| 4 | `04_flight_booking_form.png` | `/flights.html` | Select seats + book |

### 🔵 CRUD - READ (6 shots)
| # | File | URL | Action |
|---|------|-----|--------|
| 5 | `05_signin_page.png` | `/signin.html` | Login form |
| 6 | `06_ksrtc_search_results.png` | `/ksrtc.html` | Search + show buses |
| 7 | `07_train_search_results.png` | `/trains.html` | Search + show trains |
| 8 | `08_flight_search_results.png` | `/flights.html` | Search + show flights |
| 9 | `09_user_booking_history.png` | Dashboard | Show all bookings |
| 10 | `10_mobile_ticket_ksrtc.png` | `/mobile_tickets.html` | Digital ticket |

### 🔵 CRUD - UPDATE (3 shots)
| # | File | URL | Action |
|---|------|-----|--------|
| 11 | `11_cancel_ksrtc_booking.png` | Bookings page | Cancel KSRTC |
| 12 | `12_cancel_train_booking.png` | Bookings page | Cancel train |
| 13 | `13_cancel_flight_booking.png` | Bookings page | Cancel flight |

### 🔵 CRUD - DELETE (1 shot)
| # | File | URL | Action |
|---|------|-----|--------|
| 14 | `14_user_profile_delete.png` | Profile page | Show delete option |

---

### 🟢 FEATURES - Dashboards (3 shots)
| # | File | URL | Action |
|---|------|-----|--------|
| 15 | `15_user_dashboard.png` | User homepage | Login as user |
| 16 | `16_admin_dashboard_main.png` | `/admin_dashboard.html` | Login as admin |
| 17 | `17_admin_daily_revenue.png` | Admin dashboard | Scroll to revenue section |
| 18 | `18_admin_peak_hours.png` | Admin dashboard | Show peak hours chart |

### 🟢 FEATURES - Expense Tracking (2 shots)
| # | File | URL | Action |
|---|------|-----|--------|
| 19 | `19_user_daily_expenses.png` | `/expenses.html` | Select date + load |
| 20 | `20_user_monthly_expenses.png` | `/expenses.html` | Monthly chart |

### 🟢 FEATURES - Tracking (1 shot)
| # | File | URL | Action |
|---|------|-----|--------|
| 21 | `21_live_bus_tracking.png` | Tracking page | Show map |

### 🟢 FEATURES - Search (3 shots)
| # | File | URL | Action |
|---|------|-----|--------|
| 22 | `22_ksrtc_search_page.png` | `/ksrtc.html` | Empty search form |
| 23 | `23_train_search_page.png` | `/trains.html` | Empty search form |
| 24 | `24_flight_search_page.png` | `/flights.html` | Empty search form |

### 🟢 FEATURES - Seats (2 shots)
| # | File | URL | Action |
|---|------|-----|--------|
| 25 | `25_ksrtc_seat_selection.png` | After KSRTC search | Show seat map |
| 26 | `26_flight_seat_selection.png` | After flight search | Show seat map |

### 🟢 FEATURES - Reports (2 shots)
| # | File | URL | Action |
|---|------|-----|--------|
| 27 | `27_admin_popular_routes.png` | Admin dashboard | Popular routes table |
| 28 | `28_user_expense_report.png` | `/expenses.html` | Expense summary |

---

### 🟡 TRIGGERS & PROCEDURES (5 shots)
| # | File | Tool | Query |
|---|------|------|-------|
| 29 | `29_trigger_activity_log.png` | MySQL | `SELECT * FROM booking_activity_log LIMIT 20;` |
| 30 | `30_api_booking_stats.png` | DevTools | Network tab - booking stats API |
| 31 | `31_api_daily_revenue.png` | DevTools | Network tab - revenue API |
| 32 | `32_api_top_spenders.png` | DevTools | Network tab - top spenders API |
| 33 | `33_nested_query_above_avg.png` | MySQL | Query 1 from nested_queries.sql |

---

### 🟠 ADVANCED QUERIES (6 shots)
| # | File | Tool | Query |
|---|------|------|-------|
| 34 | `34_join_query_ksrtc.png` | MySQL | Query 1 from join_queries.sql |
| 35 | `35_join_query_trains.png` | MySQL | Query 2 from join_queries.sql |
| 36 | `36_join_query_flights.png` | MySQL | Query 3 from join_queries.sql |
| 37 | `37_aggregate_revenue_summary.png` | MySQL | Query 1 from aggregate_queries.sql |
| 38 | `38_aggregate_monthly_trends.png` | MySQL | Query 2 from aggregate_queries.sql |
| 39 | `39_aggregate_peak_hours.png` | MySQL | Query 3 from aggregate_queries.sql |

---

### 🔴 REPOSITORY (3 shots)
| # | File | Tool | Action |
|---|------|------|--------|
| 40 | `40_sql_files_directory.png` | File Explorer | Show sql_files folder |
| 41 | `41_github_repo_homepage.png` | Browser | GitHub main page |
| 42 | `42_github_code_structure.png` | Browser | Expanded file tree |

---

## ⚡ FASTEST CAPTURE ORDER (90 minutes)

### Session 1: User Actions (30 min) - Screenshots 1-10, 22-26
```
1. Signup (1)
2. Login (5)
3. KSRTC: Search form (22) → Results (6) → Seat map (25) → Book (2)
4. Train: Search form (23) → Results (7) → Book (3)
5. Flight: Search form (24) → Results (8) → Seat map (26) → Book (4)
6. View history (9)
7. View ticket (10)
```

### Session 2: Admin + Features (25 min) - Screenshots 15-21, 27-28
```
8. Login as user → Dashboard (15)
9. Expenses: Daily (19) → Monthly (20) → Report (28)
10. Live tracking (21) [if available]
11. Logout → Login as admin
12. Admin dashboard (16) → Revenue (17) → Peak hours (18) → Routes (27)
```

### Session 3: Cancellations + Profile (10 min) - Screenshots 11-14
```
13. Cancel KSRTC (11)
14. Cancel Train (12)
15. Cancel Flight (13)
16. Profile → Delete option (14)
```

### Session 4: Database Queries (20 min) - Screenshots 29, 33-39
```
17. Open MySQL Workbench
18. Trigger log (29)
19. Nested query (33)
20. Join queries (34-36) - Run 3 queries
21. Aggregate queries (37-39) - Run 3 queries
```

### Session 5: DevTools + GitHub (5 min) - Screenshots 30-32, 40-42
```
22. Open DevTools → Network tab
23. Reload admin dashboard → Capture APIs (30-32)
24. File Explorer → sql_files folder (40)
25. GitHub → Create repo → Upload → Screenshot (41-42)
```

---

## 🎯 QUALITY CHECKLIST

Before saving each screenshot:
- ✅ Full screen visible (no important parts cut off)
- ✅ Clear text (readable at normal size)
- ✅ Data populated (not empty tables/charts)
- ✅ No browser errors visible (unless testing errors)
- ✅ Correct filename (matching the number and description)
- ✅ Saved in right folder

---

## 💾 FOLDER STRUCTURE

Create this before starting:
```
screenshots/
├── 01_crud/
│   ├── 01_signup_page.png
│   ├── 02_ksrtc_booking_form.png
│   ├── ...
│   └── 14_user_profile_delete.png
├── 02_features/
│   ├── 15_user_dashboard.png
│   ├── ...
│   └── 28_user_expense_report.png
├── 03_triggers/
│   ├── 29_trigger_activity_log.png
│   ├── ...
│   └── 33_nested_query_above_avg.png
├── 04_queries/
│   ├── 34_join_query_ksrtc.png
│   ├── ...
│   └── 39_aggregate_peak_hours.png
└── 05_repo/
    ├── 40_sql_files_directory.png
    ├── 41_github_repo_homepage.png
    └── 42_github_code_structure.png
```

---

## 🔑 KEY CREDENTIALS

| Account Type | Username | Password |
|-------------|----------|----------|
| Admin | admin | Admin@123 |
| Test User | [your created user] | [your password] |
| MySQL | root | Darshu@2004 |

---

## 📊 REQUIRED DATA

Make sure you have:
- ✅ At least 2 KSRTC bookings
- ✅ At least 2 train bookings  
- ✅ At least 3 flight bookings
- ✅ Bookings from different dates
- ✅ Some cancelled bookings
- ✅ Some bookings for today (for daily revenue)

---

## 🚨 COMMON MISTAKES TO AVOID

1. ❌ Empty tables/charts → Make bookings first!
2. ❌ Wrong zoom level → Use 100%
3. ❌ Browser errors showing → Check console (F12)
4. ❌ Personal data visible → Use test accounts
5. ❌ Inconsistent browser → Use same browser for all
6. ❌ Missing data → Populate database first
7. ❌ Wrong filename → Follow exact naming
8. ❌ Low quality → Use PNG, not JPG
9. ❌ Partial screenshot → Capture full relevant area
10. ❌ No organization → Use folder structure

---

## ⏱️ TIME ESTIMATES

| Category | Screenshots | Time Needed |
|----------|-------------|-------------|
| CRUD Operations | 14 | 40 minutes |
| Features | 14 | 35 minutes |
| Triggers/Procedures | 5 | 15 minutes |
| Queries | 6 | 20 minutes |
| Repository | 3 | 10 minutes |
| **TOTAL** | **42** | **2 hours** |

---

## 🎬 READY TO START?

1. **Open this checklist** on second monitor or print it
2. **Start both servers** (backend + frontend)
3. **Open MySQL Workbench**
4. **Create screenshots folder structure**
5. **Begin with Session 1** (User Actions)
6. **Check off each screenshot** as you capture it
7. **Review all screenshots** before proceeding to next category

---

**Let's go! You've got this!** 💪📸
