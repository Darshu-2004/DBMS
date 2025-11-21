// Flight Booking JavaScript
const API_URL = 'http://localhost:5000/api';
let selectedFlight = null;
let selectedSeat = null;
let searchParams = {};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadAirports();
    setMinDate();
    
    document.getElementById('searchForm').addEventListener('submit', handleSearch);
    document.getElementById('passengerForm').addEventListener('submit', handleBooking);
});

function checkAuth() {
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username');
    
    if (!token) {
        window.location.href = 'login.html';
        return;
    }
    
    const userNameEl = document.getElementById('user-name');
    if (userNameEl) {
        userNameEl.textContent = `Welcome, ${username}`;
    }
}

function setMinDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('journeyDate').setAttribute('min', today);
}

async function loadAirports() {
    try {
        const response = await fetch(`${API_URL}/flights/airports`);
        const data = await response.json();
        
        if (data.success) {
            const fromSelect = document.getElementById('fromAirport');
            const toSelect = document.getElementById('toAirport');
            
            data.airports.forEach(airport => {
                const option1 = new Option(`${airport.city} (${airport.code})`, airport.code);
                const option2 = new Option(`${airport.city} (${airport.code})`, airport.code);
                fromSelect.add(option1);
                toSelect.add(option2);
            });
        }
    } catch (error) {
        console.error('Error loading airports:', error);
    }
}

async function handleSearch(e) {
    e.preventDefault();
    
    searchParams = {
        from: document.getElementById('fromAirport').value,
        to: document.getElementById('toAirport').value,
        date: document.getElementById('journeyDate').value,
        class: document.getElementById('seatClass').value
    };
    
    try {
        const response = await fetch(
            `${API_URL}/flights/search?from=${searchParams.from}&to=${searchParams.to}&date=${searchParams.date}&class=${searchParams.class}`
        );
        const data = await response.json();
        
        if (data.success) {
            displayFlights(data.flights);
            showSection('resultsSection');
        } else {
            alert('No flights found for this route');
        }
    } catch (error) {
        alert('Error searching flights: ' + error.message);
    }
}

function displayFlights(flights) {
    const container = document.getElementById('flightsList');
    
    if (flights.length === 0) {
        container.innerHTML = '<p>No flights available for this route and date.</p>';
        return;
    }
    
    container.innerHTML = flights.map(flight => `
        <div class="flight-card" onclick='selectFlight(${JSON.stringify(flight)})'>
            <div class="flight-header">
                <div class="airline-info">
                    <div class="airline-logo">✈️</div>
                    <div>
                        <div class="airline-name">${flight.airline}</div>
                        <div class="flight-number">${flight.flight_number}</div>
                    </div>
                </div>
                <span class="flight-badge">${searchParams.class}</span>
            </div>
            <div class="flight-route">
                <div class="airport">
                    <div class="airport-code">${searchParams.from}</div>
                    <div class="airport-city">${flight.from_city}</div>
                    <div class="flight-time">${flight.departure_time}</div>
                </div>
                <div class="route-line">
                    <div class="flight-duration">${Math.floor(flight.duration_mins / 60)}h ${flight.duration_mins % 60}m</div>
                </div>
                <div class="airport">
                    <div class="airport-code">${searchParams.to}</div>
                    <div class="airport-city">${flight.to_city}</div>
                    <div class="flight-time">${flight.arrival_time}</div>
                </div>
            </div>
            <div class="flight-info-row">
                <span>Available Seats: ${flight.available_seats}</span>
                <span style="font-weight: bold; color: #4facfe;">₹${flight.total_fare}</span>
            </div>
        </div>
    `).join('');
}

async function selectFlight(flight) {
    selectedFlight = flight;
    
    document.getElementById('flightDetails').innerHTML = `
        <h3>${flight.airline} ${flight.flight_number}</h3>
        <p>Route: ${flight.from_city} (${searchParams.from}) → ${flight.to_city} (${searchParams.to})</p>
        <p>Date: ${searchParams.date} | Class: ${searchParams.class}</p>
        <p>Fare: ₹${flight.base_fare} + Taxes ₹${flight.taxes} = ₹${flight.total_fare}</p>
    `;
    
    await loadSeats();
    showSection('seatsSection');
}

async function loadSeats() {
    try {
        const response = await fetch(
            `${API_URL}/flights/seats?flight_id=${selectedFlight.flight_id}&class=${searchParams.class}`
        );
        const data = await response.json();
        
        if (data.success) {
            displaySeatMap(data.seats);
        } else {
            document.getElementById('seatGrid').innerHTML = '<p>No seats available</p>';
        }
    } catch (error) {
        alert('Error loading seats: ' + error.message);
    }
}

function displaySeatMap(seats) {
    const container = document.getElementById('seatGrid');
    
    // Group seats by row
    const seatsByRow = {};
    seats.forEach(seat => {
        if (!seatsByRow[seat.row]) {
            seatsByRow[seat.row] = [];
        }
        seatsByRow[seat.row].push(seat);
    });
    
    const columns = searchParams.class === 'Business' ? ['A', 'B', 'C', 'D'] : ['A', 'B', 'C', 'D', 'E', 'F'];
    const aisleAfter = searchParams.class === 'Business' ? 2 : 3;
    
    container.innerHTML = Object.keys(seatsByRow).sort((a, b) => a - b).map(rowNum => {
        const rowSeats = seatsByRow[rowNum];
        
        return `
            <div class="seat-row">
                <div class="row-label">${rowNum}</div>
                ${columns.map((col, idx) => {
                    const seat = rowSeats.find(s => s.column === col);
                    const aisleDiv = idx === aisleAfter ? '<div class="aisle"></div>' : '';
                    
                    if (!seat) {
                        return aisleDiv + '<div class="seat" style="visibility: hidden;"></div>';
                    }
                    
                    const classes = [
                        'seat',
                        seat.is_available ? 'available' : 'booked',
                        seat.is_window ? 'window' : ''
                    ].join(' ');
                    
                    const onclick = seat.is_available ? `onclick='selectSeat(${JSON.stringify(seat)})'` : '';
                    
                    return aisleDiv + `<div class="${classes}" ${onclick}>${seat.seat_number}</div>`;
                }).join('')}
            </div>
        `;
    }).join('');
}

function selectSeat(seat) {
    if (!seat.is_available) return;
    
    selectedSeat = seat;
    document.getElementById('selectedSeatsDisplay').textContent = seat.seat_number;
    document.getElementById('totalFare').textContent = selectedFlight.total_fare;
    document.getElementById('proceedToPassenger').disabled = false;
    
    loadSeats(); // Refresh to show selection
}

function showPassengerForm() {
    if (!selectedSeat) {
        alert('Please select a seat');
        return;
    }
    showSection('passengerSection');
}

async function handleBooking(e) {
    e.preventDefault();
    
    const bookingData = {
        flight_id: selectedFlight.flight_id,
        flight_number: selectedFlight.flight_number,
        from_airport: searchParams.from,
        to_airport: searchParams.to,
        journey_date: searchParams.date,
        seat_class: searchParams.class,
        seat_number: selectedSeat.seat_number,
        seat_id: selectedSeat.seat_id,
        base_fare: selectedFlight.base_fare,
        taxes: selectedFlight.taxes,
        passenger_name: document.getElementById('passengerName').value,
        passenger_age: document.getElementById('passengerAge').value,
        passenger_gender: document.getElementById('passengerGender').value,
        passenger_phone: document.getElementById('passengerPhone').value,
        passenger_email: document.getElementById('passengerEmail').value
    };
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_URL}/flights/book`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(bookingData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayBoardingPass(data, bookingData);
            showSection('confirmationSection');
        } else {
            alert('Booking failed: ' + data.message);
        }
    } catch (error) {
        alert('Error booking flight: ' + error.message);
    }
}

function displayBoardingPass(booking, details) {
    document.getElementById('boardingPassDetails').innerHTML = `
        <div class="boarding-header">
            <h3>BOARDING PASS</h3>
            <div class="booking-ref">${booking.booking_reference}</div>
        </div>
        <div class="pass-row">
            <span class="pass-label">Passenger Name:</span>
            <span class="pass-value">${details.passenger_name.toUpperCase()}</span>
        </div>
        <div class="pass-row">
            <span class="pass-label">Flight:</span>
            <span class="pass-value">${selectedFlight.airline} ${details.flight_number}</span>
        </div>
        <div class="pass-row">
            <span class="pass-label">From:</span>
            <span class="pass-value">${details.from_airport} - ${selectedFlight.from_city}</span>
        </div>
        <div class="pass-row">
            <span class="pass-label">To:</span>
            <span class="pass-value">${details.to_airport} - ${selectedFlight.to_city}</span>
        </div>
        <div class="pass-row">
            <span class="pass-label">Date:</span>
            <span class="pass-value">${details.journey_date}</span>
        </div>
        <div class="pass-row">
            <span class="pass-label">Departure:</span>
            <span class="pass-value">${selectedFlight.departure_time}</span>
        </div>
        <div class="pass-row">
            <span class="pass-label">Seat:</span>
            <span class="pass-value">${details.seat_number} (${details.seat_class})</span>
        </div>
        <div class="pass-row">
            <span class="pass-label">Boarding Pass:</span>
            <span class="pass-value">${booking.boarding_pass}</span>
        </div>
        <div class="pass-row">
            <span class="pass-label">Total Fare:</span>
            <span class="pass-value">₹${booking.total_fare}</span>
        </div>
    `;
    
    new QRCode(document.getElementById('barcode'), {
        text: `REF:${booking.booking_reference}|FLIGHT:${details.flight_number}|SEAT:${details.seat_number}|PASSENGER:${details.passenger_name}`,
        width: 200,
        height: 200
    });
}

function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.getElementById(sectionId).classList.add('active');
}

function backToSearch() {
    showSection('searchSection');
}

function backToResults() {
    showSection('resultsSection');
}

function backToSeats() {
    showSection('seatsSection');
}

function viewAllTickets() {
    window.location.href = 'mobile_tickets.html?type=flight';
}

function newBooking() {
    window.location.reload();
}

function logout() {
    localStorage.clear();
    window.location.href = 'login.html';
}
