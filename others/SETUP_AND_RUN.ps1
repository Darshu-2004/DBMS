# ========================================
# COMPLETE SETUP AND RUN SCRIPT
# Multi-Modal Transport System with Trains & Flights
# ========================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  SETUP: Train & Flight Booking System" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Create database tables
Write-Host "[1/5] Creating train and flight database tables..." -ForegroundColor Yellow
python backend/setup_trains_flights.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to create tables!" -ForegroundColor Red
    exit 1
}

Write-Host "`n[OK] Tables created successfully!`n" -ForegroundColor Green

# Step 2: Import train data
Write-Host "[2/5] Importing train data from JSON files (300 trains)..." -ForegroundColor Yellow
Write-Host "  This will import 100 trains from each file (SF, EXP, PASS)" -ForegroundColor Gray
python backend/import_train_data.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to import train data!" -ForegroundColor Red
    exit 1
}

Write-Host "`n[OK] Train data imported!`n" -ForegroundColor Green

# Step 3: Import flight data
Write-Host "[3/5] Importing flight data from CSV (200 flights)..." -ForegroundColor Yellow
python backend/import_flight_data.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to import flight data!" -ForegroundColor Red
    exit 1
}

Write-Host "`n[OK] Flight data imported!`n" -ForegroundColor Green

# Step 4: Start Flask server
Write-Host "[4/5] Starting Flask backend server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python backend/app.py"
Start-Sleep -Seconds 3

Write-Host "[OK] Flask server started on http://localhost:5000`n" -ForegroundColor Green

# Step 5: Start FastAPI server (for routing)
Write-Host "[5/5] Starting FastAPI routing server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; uvicorn main:app --reload --port 8000"
Start-Sleep -Seconds 3

Write-Host "[OK] FastAPI server started on http://localhost:8000`n" -ForegroundColor Green

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  SETUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Database Summary:" -ForegroundColor Yellow
Write-Host "  - Train Stations: ~500+ stations from 3 JSON files" -ForegroundColor White
Write-Host "  - Trains: 300 (100 SF + 100 EXP + 100 PASS)" -ForegroundColor White
Write-Host "  - Train Coaches: ~6000 coaches with ~400,000 berths" -ForegroundColor White
Write-Host "  - Airports: ~50+ airports" -ForegroundColor White
Write-Host "  - Flights: 200 with ~34,000 seats" -ForegroundColor White

Write-Host "`nServers Running:" -ForegroundColor Yellow
Write-Host "  - Flask Backend: http://localhost:5000" -ForegroundColor White
Write-Host "  - FastAPI Routing: http://localhost:8000" -ForegroundColor White

Write-Host "`nAvailable Pages:" -ForegroundColor Yellow
Write-Host "  - Login: http://localhost:5000/login.html" -ForegroundColor White
Write-Host "  - Register: http://localhost:5000/register.html" -ForegroundColor White
Write-Host "  - Home (Map): http://localhost:5000/index.html" -ForegroundColor White
Write-Host "  - KSRTC Buses: http://localhost:5000/ksrtc.html" -ForegroundColor White
Write-Host "  - Train Booking: http://localhost:5000/trains.html" -ForegroundColor Cyan
Write-Host "  - Flight Booking: http://localhost:5000/flights.html" -ForegroundColor Cyan
Write-Host "  - My Tickets: http://localhost:5000/mobile_tickets.html" -ForegroundColor White

Write-Host "`nTEST CREDENTIALS:" -ForegroundColor Yellow
Write-Host "  Username: testuser" -ForegroundColor White
Write-Host "  Password: password123" -ForegroundColor White

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  TESTING INSTRUCTIONS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "1. Train Booking Test:" -ForegroundColor Yellow
Write-Host "   - Open http://localhost:5000/trains.html" -ForegroundColor White
Write-Host "   - Login with credentials above" -ForegroundColor White
Write-Host "   - Select stations from dropdown (e.g., NAGPUR to PUNE)" -ForegroundColor White
Write-Host "   - Choose journey date and coach class (AC-1/AC-2/AC-3/Sleeper/General)" -ForegroundColor White
Write-Host "   - Click Search Trains" -ForegroundColor White
Write-Host "   - Select a train from results" -ForegroundColor White
Write-Host "   - Choose coach and select berths (Lower/Middle/Upper)" -ForegroundColor White
Write-Host "   - Fill passenger details and book" -ForegroundColor White
Write-Host "   - Get PNR and QR code ticket!" -ForegroundColor Green

Write-Host "`n2. Flight Booking Test:" -ForegroundColor Yellow
Write-Host "   - Open http://localhost:5000/flights.html" -ForegroundColor White
Write-Host "   - Login with same credentials" -ForegroundColor White
Write-Host "   - Select airports (e.g., Delhi to Hyderabad)" -ForegroundColor White
Write-Host "   - Choose journey date and cabin class (Economy/Business)" -ForegroundColor White
Write-Host "   - Click Search Flights" -ForegroundColor White
Write-Host "   - Select flight from results" -ForegroundColor White
Write-Host "   - Choose seat from interactive seat map" -ForegroundColor White
Write-Host "   - Fill passenger details and book" -ForegroundColor White
Write-Host "   - Get boarding pass with QR code!" -ForegroundColor Green

Write-Host "`n3. View All Tickets:" -ForegroundColor Yellow
Write-Host "   - Open http://localhost:5000/mobile_tickets.html" -ForegroundColor White
Write-Host "   - Filter by transport type (KSRTC/Train/Flight)" -ForegroundColor White
Write-Host "   - View active/expired/cancelled tickets" -ForegroundColor White
Write-Host "   - Scan QR codes for verification" -ForegroundColor White

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Press Ctrl+C in server windows to stop" -ForegroundColor Yellow
Write-Host "========================================`n" -ForegroundColor Cyan

# Open browser
Write-Host "Opening train booking in browser..." -ForegroundColor Green
Start-Sleep -Seconds 2
Start-Process "http://localhost:5000/trains.html"
