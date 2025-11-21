// API URLs
const FLASK_API = 'http://localhost:5000';
const FASTAPI_URL = 'http://localhost:8000'; // Your OSMnx routing API

// Auth check
function checkAuth() {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (!token) {
        window.location.href = 'signin.html';
        return null;
    }
    
    return { token, user };
}

const auth = checkAuth();
if (auth) {
    const userNameElement = document.getElementById('user-name');
    if (userNameElement) {
        userNameElement.textContent = `Hello, ${auth.user.full_name || auth.user.username}`;
    }
}

// Logout
const logoutLink = document.getElementById('logout-link');
if (logoutLink) {
    logoutLink.addEventListener('click', (e) => {
        e.preventDefault();
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = 'signin.html';
    });
}

// ========== OSM LOCATION SEARCH ==========

let sourceLocation = null;
let destinationLocation = null;
let searchTimeout = null;

const sourceInput = document.getElementById('source');
const destInput = document.getElementById('destination');
const sourceSuggestions = document.getElementById('source-suggestions');
const destSuggestions = document.getElementById('destination-suggestions');

if (sourceInput) {
    sourceInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const query = e.target.value.trim();
        
        if (query.length < 3) {
            sourceSuggestions.classList.remove('active');
            return;
        }
        
        searchTimeout = setTimeout(() => searchLocation(query, 'source'), 500);
    });
}

if (destInput) {
    destInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const query = e.target.value.trim();
        
        if (query.length < 3) {
            destSuggestions.classList.remove('active');
            return;
        }
        
        searchTimeout = setTimeout(() => searchLocation(query, 'destination'), 500);
    });
}

async function searchLocation(query, type) {
    try {
        const response = await fetch(`${FASTAPI_URL}/api/search-location?query=${encodeURIComponent(query + ', Bangalore')}`);
        const data = await response.json();
        
        const suggestionsDiv = type === 'source' ? sourceSuggestions : destSuggestions;
        
        if (data.results && data.results.length > 0) {
            suggestionsDiv.innerHTML = data.results.map(result => `
                <div class="suggestion-item" onclick='selectLocation(${JSON.stringify(result).replace(/'/g, "&#39;")}, "${type}")'>
                    <strong>${result.display_name.split(',')[0]}</strong>
                    <small>${result.display_name}</small>
                </div>
            `).join('');
            suggestionsDiv.classList.add('active');
        } else {
            suggestionsDiv.classList.remove('active');
        }
    } catch (error) {
        console.error('Location search error:', error);
    }
}

function selectLocation(location, type) {
    if (type === 'source') {
        sourceLocation = location;
        sourceInput.value = location.display_name.split(',')[0];
        sourceSuggestions.classList.remove('active');
    } else {
        destinationLocation = location;
        destInput.value = location.display_name.split(',')[0];
        destSuggestions.classList.remove('active');
    }
}

// Close suggestions when clicking outside
document.addEventListener('click', (e) => {
    if (!e.target.closest('.form-group')) {
        sourceSuggestions.classList.remove('active');
        destSuggestions.classList.remove('active');
    }
});

// ========== TRANSPORT MODE TOGGLE ==========

const transportModeRadios = document.querySelectorAll('input[name="transport_mode"]');
const privateOptions = document.getElementById('private-options');
const publicOptions = document.getElementById('public-options');
const multiModalOptions = document.getElementById('multi-modal-options');

transportModeRadios.forEach(radio => {
    radio.addEventListener('change', (e) => {
        const mode = e.target.value;
        
        if (privateOptions) privateOptions.style.display = 'none';
        if (publicOptions) publicOptions.style.display = 'none';
        if (multiModalOptions) multiModalOptions.style.display = 'none';
        
        if (mode === 'private' && privateOptions) {
            privateOptions.style.display = 'block';
        } else if (mode === 'public' && publicOptions) {
            publicOptions.style.display = 'block';
        } else if (mode === 'multi-modal' && multiModalOptions) {
            multiModalOptions.style.display = 'block';
        }
    });
});

// ========== ROUTE SEARCH WITH YOUR ALGORITHM ==========

const searchForm = document.getElementById('route-search-form');
if (searchForm) {
    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!sourceLocation || !destinationLocation) {
            alert('Please select source and destination from the suggestions');
            return;
        }
        
        const transportMode = document.querySelector('input[name="transport_mode"]:checked').value;
        
        // Only use FastAPI for private mode (your algorithm)
        if (transportMode === 'private') {
            await searchPrivateRoutes();
        } else {
            // For public/multi-modal, use Flask backend
            await searchPublicRoutes();
        }
    });
}

async function searchPrivateRoutes() {
    try {
        const response = await fetch(`${FASTAPI_URL}/api/optimize-route`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                src_lat: sourceLocation.lat,
                src_lon: sourceLocation.lon,
                dst_lat: destinationLocation.lat,
                dst_lon: destinationLocation.lon,
                scenario: 'personal'
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            displayAlgorithmRoutes(data);
        } else {
            alert('No routes found');
        }
    } catch (error) {
        console.error('Route search error:', error);
        alert('Error finding routes. Make sure FastAPI is running on port 8000');
    }
}

async function searchPublicRoutes() {
    const formData = {
        source: sourceInput.value,
        destination: destInput.value,
        transport_mode: document.querySelector('input[name="transport_mode"]:checked').value
    };
    
    const publicMode = document.querySelector('input[name="public_mode"]:checked');
    if (publicMode) {
        formData.public_mode = publicMode.value;
    }
    
    const multiModalType = document.querySelector('input[name="multi_modal_type"]:checked');
    if (multiModalType) {
        formData.multi_modal_type = multiModalType.value;
    }
    
    try {
        const response = await fetch(`${FLASK_API}/api/routes/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${auth.token}`
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayFlaskRoutes(data.routes);
        } else {
            alert(data.message || 'Search failed');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Network error. Please try again.');
    }
}

// ========== DISPLAY ALGORITHM ROUTES ==========

function displayAlgorithmRoutes(data) {
    const resultsSection = document.getElementById('results-section');
    const routeResults = document.getElementById('route-results');
    
    if (!resultsSection || !routeResults) return;
    
    routeResults.innerHTML = '';
    
    // Display each route from your algorithm
    data.metrics.forEach((metric, index) => {
        const routeCard = document.createElement('div');
        routeCard.className = 'route-card';
        
        const routeNodes = data.routes[index];
        const incidents = data.incidents[index] || [];
        
        routeCard.innerHTML = `
            <div class="route-header">
                <div class="route-mode">
                    🚗 Route ${index + 1} - ${metric.optimization_type}
                </div>
                <span class="route-rank">#${index + 1}</span>
            </div>
            <div class="route-details">
                <div class="route-detail">
                    <strong>Distance</strong>
                    <span>${(metric.distance_km || 0).toFixed(2)} km</span>
                </div>
                <div class="route-detail">
                    <strong>Duration</strong>
                    <span>${(metric.time_mins || 0).toFixed(0)} mins</span>
                </div>
                <div class="route-detail">
                    <strong>Avg Speed</strong>
                    <span>${(metric.avg_speed_kmh || 0).toFixed(1)} km/h</span>
                </div>
                <div class="route-detail">
                    <strong>Incidents</strong>
                    <span>${incidents.length} ${incidents.length === 1 ? 'issue' : 'issues'}</span>
                </div>
            </div>
            ${incidents.length > 0 ? `
            <div class="incidents-list">
                <strong>⚠️ Traffic Incidents:</strong>
                ${incidents.slice(0, 3).map(inc => `
                    <div class="incident-badge">${inc.type || 'Traffic'}</div>
                `).join('')}
            </div>
            ` : ''}
            <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
                <button class="btn btn-primary" onclick='viewAlgorithmRoute(${index})'>
                    📍 View on Map
                </button>
            </div>
        `;
        
        routeResults.appendChild(routeCard);
    });
    
    // Store data globally for map viewing
    window.currentRouteData = data;
    
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// ========== DISPLAY FLASK ROUTES (PUBLIC/MULTI-MODAL) ==========

function displayFlaskRoutes(routes) {
    const resultsSection = document.getElementById('results-section');
    const routeResults = document.getElementById('route-results');
    
    if (!resultsSection || !routeResults) return;
    
    routeResults.innerHTML = '';
    
    routes.forEach(route => {
        const routeCard = document.createElement('div');
        routeCard.className = 'route-card';
        
        const modeEmoji = {
            'bmtc': '🚌',
            'metro': '🚇',
            'aggregator': '🚕'
        };
        
        routeCard.innerHTML = `
            <div class="route-header">
                <div class="route-mode">
                    ${modeEmoji[route.mode] || '🚗'} ${route.mode.toUpperCase()}
                </div>
            </div>
            <div class="route-details">
                <div class="route-detail">
                    <strong>Duration</strong>
                    <span>${route.duration}</span>
                </div>
                <div class="route-detail">
                    <strong>Distance</strong>
                    <span>${route.distance}</span>
                </div>
                <div class="route-detail">
                    <strong>Cost</strong>
                    <span>${route.cost}</span>
                </div>
                <div class="route-detail">
                    <strong>ETA</strong>
                    <span>${route.eta}</span>
                </div>
            </div>
            <button class="btn btn-primary" onclick="bookRoute(${route.id}, '${route.mode}')">
                Book Now
            </button>
        `;
        
        routeResults.appendChild(routeCard);
    });
    
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// ========== MAP VISUALIZATION FOR ALGORITHM ROUTES ==========

function viewAlgorithmRoute(routeIndex) {
    const data = window.currentRouteData;
    if (!data) return;
    
    // Show map section
    const mapSection = document.getElementById('map-section');
    if (!mapSection) return;
    
    mapSection.style.display = 'block';
    mapSection.scrollIntoView({ behavior: 'smooth' });
    
    // Display the pre-generated map HTML from your algorithm
    const mapContainer = document.getElementById('map-container');
    if (mapContainer && data.map_html) {
        mapContainer.innerHTML = data.map_html;
    }
}

function closeMap() {
    document.getElementById('map-section').style.display = 'none';
}

// ========== BOOKING (ONLY FOR PUBLIC/MULTI-MODAL) ==========

async function bookRoute(routeId, mode) {
    const bookingData = {
        booking_type: mode,
        source: sourceInput.value,
        destination: destInput.value,
        journey_date: new Date().toISOString().split('T')[0],
        journey_time: '10:00:00',
        passenger_count: 1,
        fare_amount: 50.00
    };
    
    try {
        const response = await fetch(`${FLASK_API}/api/bookings/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${auth.token}`
            },
            body: JSON.stringify(bookingData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`Booking confirmed! Reference: ${data.booking_reference}`);
        } else {
            alert(data.message || 'Booking failed');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Network error. Please try again.');
    }
}

// ========== MY BOOKINGS ==========

const myBookingsLink = document.getElementById('my-bookings-link');
const bookingsModal = document.getElementById('bookings-modal');
const closeModal = document.querySelector('.close');

if (myBookingsLink) {
    myBookingsLink.addEventListener('click', async (e) => {
        e.preventDefault();
        await loadMyBookings();
        if (bookingsModal) bookingsModal.style.display = 'block';
    });
}

if (closeModal) {
    closeModal.addEventListener('click', () => {
        if (bookingsModal) bookingsModal.style.display = 'none';
    });
}

async function loadMyBookings() {
    try {
        const response = await fetch(`${FLASK_API}/api/bookings/my`, {
            headers: {'Authorization': `Bearer ${auth.token}`}
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayBookings(data.bookings);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function displayBookings(bookings) {
    const bookingsList = document.getElementById('bookings-list');
    
    if (!bookingsList) return;
    
    if (bookings.length === 0) {
        bookingsList.innerHTML = '<p>No bookings found.</p>';
        return;
    }
    
    bookingsList.innerHTML = '';
    
    bookings.forEach(booking => {
        const bookingCard = document.createElement('div');
        bookingCard.className = 'route-card';
        bookingCard.innerHTML = `
            <div class="route-header">
                <div>
                    <strong>${booking.booking_type.toUpperCase()}</strong>
                    <div style="font-size: 0.9rem; color: #6b7280;">
                        Ref: ${booking.booking_reference}
                    </div>
                </div>
                <span class="badge">${booking.booking_status}</span>
            </div>
            <div style="margin-top: 1rem;">
                <p><strong>From:</strong> ${booking.source}</p>
                <p><strong>To:</strong> ${booking.destination}</p>
                <p><strong>Date:</strong> ${booking.journey_date}</p>
                <p><strong>Fare:</strong> ₹${booking.fare_amount || 'N/A'}</p>
            </div>
        `;
        bookingsList.appendChild(bookingCard);
    });
}

// Service cards handler
function openService(serviceType) {
    alert(`${serviceType.toUpperCase()} booking feature coming soon!`);
}

// Make functions global
window.openService = openService;
window.bookRoute = bookRoute;
window.selectLocation = selectLocation;
window.viewAlgorithmRoute = viewAlgorithmRoute;
window.closeMap = closeMap;
