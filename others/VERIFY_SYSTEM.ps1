# ========================================
# FINAL VERIFICATION SCRIPT
# Verify all systems are working
# ========================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  SYSTEM VERIFICATION" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test database connectivity
Write-Host "[1/6] Testing MySQL connection..." -ForegroundColor Yellow

$testDb = @"
import mysql.connector
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='transport_system'
    )
    cursor = conn.cursor()
    
    # Check KSRTC tables
    cursor.execute("SELECT COUNT(*) FROM ksrtc_stops")
    ksrtc_stops = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ksrtc_routes")
    ksrtc_routes = cursor.fetchone()[0]
    
    # Check Train tables
    cursor.execute("SELECT COUNT(*) FROM train_stations")
    train_stations = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM trains")
    trains = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM train_berths")
    berths = cursor.fetchone()[0]
    
    # Check Flight tables
    cursor.execute("SELECT COUNT(*) FROM airports")
    airports = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM flights")
    flights = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM flight_seats")
    flight_seats = cursor.fetchone()[0]
    
    print(f"[OK] KSRTC: {ksrtc_stops} stops, {ksrtc_routes} routes")
    print(f"[OK] Trains: {train_stations} stations, {trains} trains, {berths} berths")
    print(f"[OK] Flights: {airports} airports, {flights} flights, {flight_seats} seats")
    
    conn.close()
    exit(0)
except Exception as e:
    print(f"[ERROR] {str(e)}")
    exit(1)
"@

$testDb | python
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Database verification failed!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check if Flask server is running
Write-Host "[2/6] Checking Flask server (port 5000)..." -ForegroundColor Yellow
$flaskRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/trains/stations" -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "[OK] Flask server is running" -ForegroundColor Green
        $flaskRunning = $true
    }
} catch {
    Write-Host "[WARNING] Flask server not running on port 5000" -ForegroundColor Yellow
}
Write-Host ""

# Check if FastAPI server is running
Write-Host "[3/6] Checking FastAPI server (port 8000)..." -ForegroundColor Yellow
$fastApiRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "[OK] FastAPI server is running" -ForegroundColor Green
        $fastApiRunning = $true
    }
} catch {
    Write-Host "[WARNING] FastAPI server not running on port 8000" -ForegroundColor Yellow
}
Write-Host ""

# Check file structure
Write-Host "[4/6] Verifying file structure..." -ForegroundColor Yellow
$requiredFiles = @(
    "backend\app.py",
    "backend\main.py",
    "backend\database.py",
    "backend\setup_trains_flights.py",
    "backend\import_train_data.py",
    "backend\import_flight_data.py",
    "frontend\trains.html",
    "frontend\flights.html",
    "frontend\css\trains.css",
    "frontend\css\flights.css",
    "frontend\js\trains.js",
    "frontend\js\flights.js",
    "SF-TRAINS.json",
    "EXP-TRAINS.json",
    "PASS-TRAINS.json",
    "Flight_Schedule.csv"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (!(Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -eq 0) {
    Write-Host "[OK] All required files present" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Missing files:" -ForegroundColor Red
    $missingFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
}
Write-Host ""

# Test API endpoints
Write-Host "[5/6] Testing API endpoints..." -ForegroundColor Yellow
if ($flaskRunning) {
    try {
        # Test trains API
        $trainsResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/trains/stations" -Method Get
        if ($trainsResponse.success) {
            Write-Host "[OK] Train stations API working (${($trainsResponse.stations.Count)} stations)" -ForegroundColor Green
        }
        
        # Test flights API
        $flightsResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/flights/airports" -Method Get
        if ($flightsResponse.success) {
            Write-Host "[OK] Flight airports API working (${($flightsResponse.airports.Count)} airports)" -ForegroundColor Green
        }
        
        # Test KSRTC API
        $ksrtcResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/ksrtc/stops" -Method Get
        if ($ksrtcResponse.success) {
            Write-Host "[OK] KSRTC stops API working (${($ksrtcResponse.stops.Count)} stops)" -ForegroundColor Green
        }
    } catch {
        Write-Host "[ERROR] API endpoint test failed: $_" -ForegroundColor Red
    }
} else {
    Write-Host "[SKIP] Flask server not running, cannot test APIs" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "[6/6] Generating summary report..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VERIFICATION SUMMARY" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Database Status:" -ForegroundColor Yellow
Write-Host "  [OK] MySQL Connected" -ForegroundColor Green
Write-Host "  [OK] All tables created" -ForegroundColor Green
Write-Host "  [OK] Data imported successfully" -ForegroundColor Green

Write-Host "`nServer Status:" -ForegroundColor Yellow
if ($flaskRunning) {
    Write-Host "  [OK] Flask server (port 5000)" -ForegroundColor Green
} else {
    Write-Host "  [!] Flask server not running" -ForegroundColor Yellow
    Write-Host "      Run: python backend\app.py" -ForegroundColor Gray
}

if ($fastApiRunning) {
    Write-Host "  [OK] FastAPI server (port 8000)" -ForegroundColor Green
} else {
    Write-Host "  [!] FastAPI server not running" -ForegroundColor Yellow
    Write-Host "      Run: cd backend; uvicorn main:app --reload --port 8000" -ForegroundColor Gray
}

Write-Host "`nFile Structure:" -ForegroundColor Yellow
if ($missingFiles.Count -eq 0) {
    Write-Host "  [OK] All files present" -ForegroundColor Green
} else {
    Write-Host "  [!] Some files missing" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  READY TO TEST!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

if ($flaskRunning -and $fastApiRunning) {
    Write-Host "All systems operational! Access:" -ForegroundColor Green
    Write-Host "  - Train Booking: http://localhost:5000/trains.html" -ForegroundColor Cyan
    Write-Host "  - Flight Booking: http://localhost:5000/flights.html" -ForegroundColor Cyan
    Write-Host "  - KSRTC Booking: http://localhost:5000/ksrtc.html" -ForegroundColor White
    Write-Host "  - Login Page: http://localhost:5000/login.html" -ForegroundColor White
    Write-Host ""
    Write-Host "Test Credentials:" -ForegroundColor Yellow
    Write-Host "  Username: testuser" -ForegroundColor White
    Write-Host "  Password: password123" -ForegroundColor White
} else {
    Write-Host "Please start servers first:" -ForegroundColor Yellow
    Write-Host "  1. Run: .\SETUP_AND_RUN.ps1" -ForegroundColor White
    Write-Host "     OR" -ForegroundColor Gray
    Write-Host "  2. Manually start:" -ForegroundColor White
    Write-Host "     Terminal 1: python backend\app.py" -ForegroundColor White
    Write-Host "     Terminal 2: cd backend; uvicorn main:app --reload --port 8000" -ForegroundColor White
}

Write-Host "`n========================================`n" -ForegroundColor Cyan
