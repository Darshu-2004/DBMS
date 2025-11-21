// Train Booking JavaScript
const API_URL = 'http://localhost:5000/api';
let selectedTrain = null;
let selectedCoach = null;
let selectedBerths = [];
let searchParams = {};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadStations();
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

async function loadStations() {
    try {
        const response = await fetch(`${API_URL}/trains/stations`);
        const data = await response.json();
        
        if (data.success) {
            const fromSelect = document.getElementById('fromStation');
            const toSelect = document.getElementById('toStation');
            
            data.stations.forEach(station => {
                const option1 = new Option(`${station.name} (${station.code})`, station.code);
                const option2 = new Option(`${station.name} (${station.code})`, station.code);
                fromSelect.add(option1);
                toSelect.add(option2);
            });
        }
    } catch (error) {
        console.error('Error loading stations:', error);
    }
}

async function handleSearch(e) {
    e.preventDefault();
    
    searchParams = {
        from: document.getElementById('fromStation').value,
        to: document.getElementById('toStation').value,
        date: document.getElementById('journeyDate').value,
        class: document.getElementById('coachClass').value
    };
    
    try {
        const response = await fetch(
            `${API_URL}/trains/search?from=${searchParams.from}&to=${searchParams.to}&date=${searchParams.date}&class=${searchParams.class}`
        );
        const data = await response.json();
        
        if (data.success) {
            displayTrains(data.trains);
            showSection('resultsSection');
        } else {
            alert('No trains found for this route');
        }
    } catch (error) {
        alert('Error searching trains: ' + error.message);
    }
}

function displayTrains(trains) {
    const container = document.getElementById('trainsList');
    
    if (trains.length === 0) {
        container.innerHTML = '<p>No trains available for this route and date.</p>';
        return;
    }
    
    container.innerHTML = trains.map(train => `
        <div class="train-card" onclick='selectTrain(${JSON.stringify(train)})'>
            <div class="train-header">
                <div>
                    <div class="train-number">${train.train_number}</div>
                    <div class="train-name">${train.train_name}</div>
                </div>
                <span class="train-badge">${train.train_type}</span>
            </div>
            <div class="train-route">
                <div class="station">
                    <div class="station-name">${searchParams.from}</div>
                    <div class="station-time">${train.from_departure}</div>
                </div>
                <div class="route-arrow">→</div>
                <div class="station">
                    <div class="station-name">${searchParams.to}</div>
                    <div class="station-time">${train.to_arrival}</div>
                </div>
            </div>
            <div class="train-info-row">
                <span>Distance: ${train.distance_km} km</span>
                <span>Class: ${searchParams.class}</span>
                <span style="font-weight: bold; color: #667eea;">₹${train.fare}</span>
            </div>
        </div>
    `).join('');
}

async function selectTrain(train) {
    selectedTrain = train;
    
    document.getElementById('trainDetails').innerHTML = `
        <h3>${train.train_number} - ${train.train_name}</h3>
        <p>Route: ${searchParams.from} → ${searchParams.to} | Date: ${searchParams.date}</p>
        <p>Base Fare: ₹${train.fare}</p>
    `;
    
    await loadCoaches();
    showSection('seatsSection');
}

async function loadCoaches() {
    try {
        const response = await fetch(
            `${API_URL}/trains/coaches?train_id=${selectedTrain.train_id}&coach_type=${searchParams.class}`
        );
        const data = await response.json();
        
        if (data.success && data.coaches.length > 0) {
            displayCoachSelector(data.coaches);
            displayBerths(data.coaches[0]);
            selectedCoach = data.coaches[0];
        } else {
            document.getElementById('seatMap').innerHTML = '<p>No coaches available for this class</p>';
        }
    } catch (error) {
        alert('Error loading coaches: ' + error.message);
    }
}

function displayCoachSelector(coaches) {
    const container = document.getElementById('coachSelector');
    container.innerHTML = '<h3>Select Coach:</h3>' + coaches.map((coach, idx) => `
        <button class="coach-btn ${idx === 0 ? 'active' : ''}" 
                onclick='selectCoach(${JSON.stringify(coach)})'>
            ${coach.coach_number}
        </button>
    `).join('');
}

function selectCoach(coach) {
    selectedCoach = coach;
    selectedBerths = [];
    updateSelectedDisplay();
    
    document.querySelectorAll('.coach-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    displayBerths(coach);
}

function displayBerths(coach) {
    const container = document.getElementById('seatMap');
    container.innerHTML = `
        <h3>Coach ${coach.coach_number} - Select Berth</h3>
        <div class="berth-layout">
            ${coach.berths.map(berth => `
                <div class="berth ${berth.is_available ? 'available' : 'booked'}" 
                     onclick='toggleBerth(${JSON.stringify(berth)})'>
                    ${berth.berth_number}
                    <span class="berth-type">${berth.berth_type}</span>
                </div>
            `).join('')}
        </div>
    `;
}

function toggleBerth(berth) {
    if (!berth.is_available) return;
    
    const index = selectedBerths.findIndex(b => b.berth_id === berth.berth_id);
    
    if (index > -1) {
        selectedBerths.splice(index, 1);
    } else {
        if (selectedBerths.length >= 6) {
            alert('Maximum 6 berths can be selected');
            return;
        }
        selectedBerths.push(berth);
    }
    
    updateSelectedDisplay();
    displayBerths(selectedCoach);
}

function updateSelectedDisplay() {
    const berthNumbers = selectedBerths.map(b => b.berth_number).join(', ');
    document.getElementById('selectedSeatsDisplay').textContent = berthNumbers || 'None';
    
    const totalFare = selectedTrain.fare * Math.max(1, selectedBerths.length) + 40;
    document.getElementById('totalFare').textContent = totalFare.toFixed(2);
    
    document.getElementById('proceedToPassenger').disabled = selectedBerths.length === 0;
}

function showPassengerForm() {
    if (selectedBerths.length === 0) {
        alert('Please select at least one berth');
        return;
    }
    showSection('passengerSection');
}

async function handleBooking(e) {
    e.preventDefault();
    
    const bookingData = {
        train_id: selectedTrain.train_id,
        train_number: selectedTrain.train_number,
        from_station: searchParams.from,
        to_station: searchParams.to,
        journey_date: searchParams.date,
        coach_type: searchParams.class,
        berth_numbers: selectedBerths.map(b => b.berth_number),
        berth_ids: selectedBerths.map(b => b.berth_id),
        base_fare: selectedTrain.fare,
        passenger_name: document.getElementById('passengerName').value,
        passenger_age: document.getElementById('passengerAge').value,
        passenger_gender: document.getElementById('passengerGender').value,
        passenger_phone: document.getElementById('passengerPhone').value,
        passenger_email: document.getElementById('passengerEmail').value
    };
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_URL}/trains/book`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(bookingData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayConfirmation(data, bookingData);
            showSection('confirmationSection');
        } else {
            alert('Booking failed: ' + data.message);
        }
    } catch (error) {
        alert('Error booking ticket: ' + error.message);
    }
}

function displayConfirmation(booking, details) {
    document.getElementById('ticketDetails').innerHTML = `
        <div class="pnr-number">PNR: ${booking.pnr}</div>
        <div class="ticket-row">
            <span class="ticket-label">Ticket Number:</span>
            <span class="ticket-value">${booking.ticket_number}</span>
        </div>
        <div class="ticket-row">
            <span class="ticket-label">Train:</span>
            <span class="ticket-value">${details.train_number}</span>
        </div>
        <div class="ticket-row">
            <span class="ticket-label">Route:</span>
            <span class="ticket-value">${details.from_station} → ${details.to_station}</span>
        </div>
        <div class="ticket-row">
            <span class="ticket-label">Date:</span>
            <span class="ticket-value">${details.journey_date}</span>
        </div>
        <div class="ticket-row">
            <span class="ticket-label">Passenger:</span>
            <span class="ticket-value">${details.passenger_name}</span>
        </div>
        <div class="ticket-row">
            <span class="ticket-label">Coach/Berth:</span>
            <span class="ticket-value">${selectedCoach.coach_number} / ${details.berth_numbers.join(', ')}</span>
        </div>
        <div class="ticket-row">
            <span class="ticket-label">Total Fare:</span>
            <span class="ticket-value">₹${booking.total_fare}</span>
        </div>
    `;
    
    new QRCode(document.getElementById('qrCode'), {
        text: `PNR:${booking.pnr}|TRAIN:${details.train_number}|PASSENGER:${details.passenger_name}`,
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
    window.location.href = 'mobile_tickets.html?type=train';
}

function newBooking() {
    window.location.reload();
}

function logout() {
    localStorage.clear();
    window.location.href = 'login.html';
}
