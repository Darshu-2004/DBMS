// KSRTC Booking System JavaScript
const API_URL = 'http://localhost:5000';

let selectedBus = null;
let selectedSeats = [];
let searchParams = {};
let auth = null;

// Check authentication
function checkAuth() {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (!token) {
        window.location.href = 'signin.html';
        return null;
    }
    
    return { token, user };
}

auth = checkAuth();
if (auth && document.getElementById('user-name')) {
    document.getElementById('user-name').textContent = `Hello, ${auth.user.full_name || auth.user.username}`;
}

// Logout
document.getElementById('logout-link')?.addEventListener('click', (e) => {
    e.preventDefault();
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = 'signin.html';
});

// Load stops on page load
window.addEventListener('DOMContentLoaded', loadStops);

async function loadStops() {
    try {
        const response = await fetch(`${API_URL}/api/ksrtc/stops`);
        const data = await response.json();
        
        const fromSelect = document.getElementById('from-stop');
        const toSelect = document.getElementById('to-stop');
        
        data.stops.forEach(stop => {
            fromSelect.add(new Option(stop.stop_name, stop.stop_name));
            toSelect.add(new Option(stop.stop_name, stop.stop_name));
        });
        
        // Set min date to today
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('journey-date').min = today;
        document.getElementById('journey-date').value = today;
        
    } catch (error) {
        console.error('Error loading stops:', error);
        alert('Failed to load bus stops. Please refresh the page.');
    }
}

// Search buses
document.getElementById('bus-search-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    searchParams = {
        from: document.getElementById('from-stop').value,
        to: document.getElementById('to-stop').value,
        date: document.getElementById('journey-date').value
    };
    
    if (searchParams.from === searchParams.to) {
        alert('Source and destination cannot be the same!');
        return;
    }
    
    await searchBuses(searchParams);
});

async function searchBuses(params) {
    try {
        const response = await fetch(`${API_URL}/api/ksrtc/search?from=${params.from}&to=${params.to}&date=${params.date}`);
        const data = await response.json();
        
        if (data.success && data.buses.length > 0) {
            displayBuses(data.buses);
            document.getElementById('buses-section').style.display = 'block';
            document.getElementById('buses-section').scrollIntoView({ behavior: 'smooth' });
        } else {
            alert('No buses found for this route. Please try another route or date.');
        }
    } catch (error) {
        console.error('Error searching buses:', error);
        alert('Error searching buses. Please try again.');
    }
}

function displayBuses(buses) {
    const busesList = document.getElementById('buses-list');
    busesList.innerHTML = '';
    
    buses.forEach(bus => {
        const busCard = document.createElement('div');
        busCard.className = 'bus-card';
        busCard.innerHTML = `
            <div class="bus-card-header">
                <div>
                    <div class="bus-type-badge">${bus.bus_type}</div>
                    <div class="bus-number">${bus.bus_number}</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.5rem; font-weight: 700; color: #10b981;">₹${bus.base_fare}</div>
                    <div style="font-size: 0.85rem; color: #6b7280;">${bus.available_seats} seats available</div>
                </div>
            </div>
            <div class="bus-details-grid">
                <div class="bus-detail-item">
                    <strong>Departure</strong>
                    <span>${bus.departure_time}</span>
                </div>
                <div class="bus-detail-item">
                    <strong>Arrival (Est.)</strong>
                    <span>${bus.arrival_time || 'N/A'}</span>
                </div>
                <div class="bus-detail-item">
                    <strong>Total Seats</strong>
                    <span>${bus.total_seats}</span>
                </div>
                <div class="bus-detail-item">
                    <strong>Route</strong>
                    <span>${bus.route_number}</span>
                </div>
            </div>
            <div class="bus-amenities">
                ${bus.ac_available ? '<span class="amenity-badge">❄️ AC</span>' : ''}
                <span class="amenity-badge">💺 ${bus.seater_seats} Seater</span>
                ${bus.sleeper_seats > 0 ? `<span class="amenity-badge">🛏️ ${bus.sleeper_seats} Sleeper</span>` : ''}
            </div>
            <button class="btn btn-primary select-bus-btn" onclick='selectBus(${JSON.stringify(bus)})'>
                Select Seats →
            </button>
        `;
        busesList.appendChild(busCard);
    });
}

function selectBus(bus) {
    selectedBus = bus;
    selectedSeats = [];
    loadSeats(bus.schedule_id, searchParams.date);
    
    document.getElementById('selected-bus-info').textContent = 
        `${bus.bus_number} | ${bus.bus_type} | ${searchParams.from} → ${searchParams.to}`;
    
    document.getElementById('bus-details').innerHTML = `
        <div style="margin-top: 1rem;">
            <p><strong>Departure:</strong> ${bus.departure_time}</p>
            <p><strong>Date:</strong> ${searchParams.date}</p>
            <p><strong>Base Fare:</strong> ₹${bus.base_fare} per seat</p>
        </div>
    `;
    
    document.getElementById('seat-selection-section').style.display = 'block';
    document.getElementById('seat-selection-section').scrollIntoView({ behavior: 'smooth' });
}

async function loadSeats(scheduleId, journeyDate) {
    try {
        const response = await fetch(`${API_URL}/api/ksrtc/seats?schedule_id=${scheduleId}&date=${journeyDate}`);
        const data = await response.json();
        
        if (data.success) {
            displaySeatMap(data.seats);
        }
    } catch (error) {
        console.error('Error loading seats:', error);
        alert('Error loading seats. Please try again.');
    }
}

function displaySeatMap(seats) {
    const seatMap = document.getElementById('seat-map');
    seatMap.innerHTML = '';
    seatMap.className = 'seat-map';
    
    // Add driver seat
    const driverSeat = document.createElement('div');
    driverSeat.className = 'seat driver';
    driverSeat.innerHTML = '🚗';
    driverSeat.style.gridColumn = '1 / 2';
    seatMap.appendChild(driverSeat);
    
    // Add empty space
    const emptySpace = document.createElement('div');
    emptySpace.style.gridColumn = '2 / 5';
    seatMap.appendChild(emptySpace);
    
    // Add seats
    seats.forEach(seat => {
        const seatDiv = document.createElement('div');
        seatDiv.className = `seat ${seat.is_booked ? 'booked' : 'available'}`;
        seatDiv.textContent = seat.seat_number;
        seatDiv.dataset.seatNumber = seat.seat_number;
        
        if (!seat.is_booked) {
            seatDiv.onclick = () => toggleSeat(seat.seat_number);
        }
        
        seatMap.appendChild(seatDiv);
    });
    
    updateSeatSelection();
}

function toggleSeat(seatNumber) {
    const index = selectedSeats.indexOf(seatNumber);
    
    if (index > -1) {
        selectedSeats.splice(index, 1);
    } else {
        if (selectedSeats.length >= 6) {
            alert('You can select maximum 6 seats at a time');
            return;
        }
        selectedSeats.push(seatNumber);
    }
    
    // Update UI
    document.querySelectorAll('.seat').forEach(seat => {
        const seatNum = seat.dataset.seatNumber;
        if (seatNum && selectedSeats.includes(seatNum)) {
            seat.classList.remove('available');
            seat.classList.add('selected');
        } else if (seatNum && seat.classList.contains('selected')) {
            seat.classList.remove('selected');
            seat.classList.add('available');
        }
    });
    
    updateSeatSelection();
}

function updateSeatSelection() {
    const display = document.getElementById('selected-seats-display');
    const proceedBtn = document.getElementById('proceed-booking-btn');
    
    if (selectedSeats.length === 0) {
        display.innerHTML = 'No seats selected';
        document.getElementById('total-fare').textContent = '₹0';
        proceedBtn.disabled = true;
    } else {
        display.innerHTML = selectedSeats.map(seat => 
            `<span class="seat-tag">Seat ${seat}</span>`
        ).join('');
        
        const totalFare = selectedBus.base_fare * selectedSeats.length;
        document.getElementById('total-fare').textContent = `₹${totalFare}`;
        proceedBtn.disabled = false;
    }
}

// Proceed to passenger details
document.getElementById('proceed-booking-btn')?.addEventListener('click', () => {
    if (selectedSeats.length === 0) {
        alert('Please select at least one seat');
        return;
    }
    
    // Update booking review
    const totalFare = selectedBus.base_fare * selectedSeats.length;
    document.getElementById('booking-review-details').innerHTML = `
        <div class="review-item">
            <span>Route:</span>
            <strong>${searchParams.from} → ${searchParams.to}</strong>
        </div>
        <div class="review-item">
            <span>Bus:</span>
            <strong>${selectedBus.bus_number} (${selectedBus.bus_type})</strong>
        </div>
        <div class="review-item">
            <span>Journey Date:</span>
            <strong>${searchParams.date}</strong>
        </div>
        <div class="review-item">
            <span>Departure:</span>
            <strong>${selectedBus.departure_time}</strong>
        </div>
        <div class="review-item">
            <span>Seats:</span>
            <strong>${selectedSeats.join(', ')}</strong>
        </div>
        <div class="review-item" style="font-size: 1.2rem; color: #10b981;">
            <span>Total Fare:</span>
            <strong>₹${totalFare}</strong>
        </div>
    `;
    
    document.getElementById('passenger-section').style.display = 'block';
    document.getElementById('passenger-section').scrollIntoView({ behavior: 'smooth' });
});

// Back buttons
document.getElementById('back-to-buses-btn')?.addEventListener('click', () => {
    document.getElementById('seat-selection-section').style.display = 'none';
    document.getElementById('buses-section').scrollIntoView({ behavior: 'smooth' });
});

document.getElementById('back-to-seats-btn')?.addEventListener('click', () => {
    document.getElementById('passenger-section').style.display = 'none';
    document.getElementById('seat-selection-section').scrollIntoView({ behavior: 'smooth' });
});

// Submit booking
document.getElementById('passenger-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const bookingData = {
        schedule_id: selectedBus.schedule_id,
        journey_date: searchParams.date,
        boarding_stop: searchParams.from,
        destination_stop: searchParams.to,
        seat_numbers: selectedSeats.join(','),
        passenger_name: document.getElementById('passenger-name').value,
        passenger_age: document.getElementById('passenger-age').value,
        passenger_gender: document.getElementById('passenger-gender').value,
        passenger_phone: document.getElementById('passenger-phone').value,
        passenger_email: document.getElementById('passenger-email').value || '',
        total_fare: selectedBus.base_fare * selectedSeats.length
    };
    
    try {
        const response = await fetch(`${API_URL}/api/ksrtc/book`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${auth.token}`
            },
            body: JSON.stringify(bookingData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showConfirmation(data.booking);
        } else {
            alert(data.message || 'Booking failed. Please try again.');
        }
    } catch (error) {
        console.error('Booking error:', error);
        alert('Booking failed. Please try again.');
    }
});

function showConfirmation(booking) {
    document.getElementById('confirmation-details').innerHTML = `
        <div style="text-align: center; margin: 2rem 0;">
            <div style="font-size: 1.5rem; font-weight: 700; margin-bottom: 1rem;">
                Booking Reference: ${booking.booking_reference}
            </div>
            <div style="font-size: 1.2rem; color: #6b7280;">
                Ticket Number: ${booking.ticket_number}
            </div>
        </div>
        <div class="review-item">
            <span>Passenger:</span>
            <strong>${booking.passenger_name}</strong>
        </div>
        <div class="review-item">
            <span>Route:</span>
            <strong>${booking.boarding_stop} → ${booking.destination_stop}</strong>
        </div>
        <div class="review-item">
            <span>Bus:</span>
            <strong>${selectedBus.bus_number}</strong>
        </div>
        <div class="review-item">
            <span>Journey Date:</span>
            <strong>${booking.journey_date}</strong>
        </div>
        <div class="review-item">
            <span>Seats:</span>
            <strong>${booking.seat_numbers}</strong>
        </div>
        <div class="review-item" style="font-size: 1.3rem; color: #10b981;">
            <span>Amount Paid:</span>
            <strong>₹${booking.total_fare}</strong>
        </div>
    `;
    
    document.getElementById('passenger-section').style.display = 'none';
    document.getElementById('confirmation-section').style.display = 'block';
    document.getElementById('confirmation-section').scrollIntoView({ behavior: 'smooth' });
}

// Make functions global
window.selectBus = selectBus;
window.toggleSeat = toggleSeat;
