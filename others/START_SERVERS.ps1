#!/usr/bin/env pwsh
# ========================================
# START ALL SERVERS
# ========================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  STARTING TRANSPORT BOOKING SYSTEM" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Get the script directory
$PROJECT_ROOT = $PSScriptRoot

Write-Host "[1/3] Starting Flask Backend Server (Port 5000)..." -ForegroundColor Yellow
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$PROJECT_ROOT\backend'; python app.py"
Start-Sleep -Seconds 3

Write-Host "[2/3] Starting FastAPI Routing Server (Port 8000)..." -ForegroundColor Yellow
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$PROJECT_ROOT\New folder (3)\backend'; python -m uvicorn api:app --reload --port 8000"
Start-Sleep -Seconds 3

Write-Host "[3/3] Opening Browser..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

# Open all booking pages
Start-Process "http://localhost:5000/trains.html"
Start-Sleep -Seconds 1
Start-Process "http://localhost:5000/flights.html"
Start-Sleep -Seconds 1
Start-Process "http://localhost:5000/index.html"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  ✓ ALL SERVERS STARTED!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Access Points:" -ForegroundColor White
Write-Host "  🚂 Trains:  http://localhost:5000/trains.html" -ForegroundColor Cyan
Write-Host "  ✈️  Flights: http://localhost:5000/flights.html" -ForegroundColor Cyan
Write-Host "  🚌 KSRTC:   http://localhost:5000/index.html" -ForegroundColor Cyan
Write-Host "  🎫 Tickets: http://localhost:5000/mobile_tickets.html" -ForegroundColor Cyan
Write-Host "  🎛️  Admin:   http://localhost:5000/admin.html" -ForegroundColor Cyan

Write-Host "`nLogin Credentials:" -ForegroundColor White
Write-Host "  User:  testuser / password123" -ForegroundColor Yellow
Write-Host "  Admin: admin / admin123" -ForegroundColor Yellow

Write-Host "`nPress Ctrl+C in each terminal window to stop servers`n" -ForegroundColor Gray
