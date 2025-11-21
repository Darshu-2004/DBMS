// API Base URL
const API_BASE_URL = 'http://localhost:5000/api';

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

// Initialize
const auth = checkAuth();
if (!auth) {
    // Redirect handled in checkAuth
} else {
    // Display user name
    const userNameElement = document.getElementById('user-name');
    if (userNameElement) {
        userNameElement.textContent = `Hello, ${auth.user.full_name || auth.user.username}`;
    }
}

// Logout handler
const logoutLink = document.getElementById('logout-link');
if (logoutLink) {
    logoutLink.addEventListener('click', (e) => {
        e.preventDefault();
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = 'signin.html';
    });
}

// Transport mode toggle
const transportModeRadios = document.querySelectorAll('input[name="transport_mode"]');
const privateOptions = document.getElementById('private-options');
const publicOptions = document.getElementById('public-options');
const multiModalOptions = document.getElementById('multi-modal-options');

transportModeRadios.forEach(radio => {
    radio.addEventListener('change', (e) => {
        const mode = e.target.value;
        
        // Hide all options
        if (privateOptions) privateOptions.style.display = 'none';
        if (publicOptions) publicOptions.style.display = 'none';
        if (multiModalOptions) multiModalOptions.style.display = 'none';
        
        // Show selected mode options
        if (mode === 'private' && privateOptions) {
            privateOptions.style.display = 'block';
        } else if (mode === 'public' && publicOptions) {
            publicOptions.style.display = 'block';
        } else if (mode === 'multi-modal') {
            if (privateOptions) privateOptions.style.display = 'block';
            if (publicOptions) publicOptions.style.display = 'block';
            if (multiModalOptions) multiModalOptions.style.display = 'block';
        }
    });
});

// Route Search Handler
const routeSearchForm = document.getElementById('route-search-form');
if (routeSearchForm) {
    routeSearchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const transportMode = document.querySelector('input[name="transport_mode"]:checked').value;
        
        const formData = {
            source: document.getElementById('source').value,
            destination: document.getElementById('destination').value,
            transport_mode: transportMode,
            preference_type: document.querySelector('input[name="preference_type"]:checked').value
        };
        
        // Add mode-specific data
        if (transportMode === 'private' || transportMode === 'multi-modal') {
            const privateModeElement = document.querySelector('input[name="private_mode"]:checked');
            if (privateModeElement) {
                formData.private_mode = privateModeElement.value;
            }
        }
        
        if (transportMode === 'public' || transportMode === 'multi-modal') {
            const publicModeElement = document.querySelector('input[name="public_mode"]:checked');
            if (publicModeElement) {
                formData.public_mode = publicModeElement.value;
            }
        }
        
        if (transportMode === 'multi-modal') {
            const multiModalElement = document.querySelector('input[name="multi_modal_type"]:checked');
            if (multiModalElement) {
                formData.multi_modal_type = multiModalElement.value;
            }
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/routes/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${auth.token}`
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                displayRoutes(data.routes);
            } else {
                alert(data.message || 'Search failed');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Network error. Please try again.');
        }
    });
}

// Display routes
function displayRoutes(routes) {
    const resultsSection = document.getElementById('results-section');
    const routeResults = document.getElementById('route-results');
    
    if (!resultsSection || !routeResults) return;
    
    routeResults.innerHTML = '';
    
    routes.forEach(route => {
        const routeCard = document.createElement('div');
        routeCard.className = 'route-card';
        
        const modeEmoji = {
            'bike': '🏍️',
            'car': '🚗',
            'walk': '🚶',
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
                ${route.fuel_cost ? `
                <div class="route-detail">
                    <strong>Fuel Cost</strong>
                    <span>${route.fuel_cost}</span>
                </div>
                ` : ''}
                <div class="route-detail">
                    <strong>ETA</strong>
                    <span>${route.eta}</span>
                </div>
            </div>
            <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
                ${route.source_coords && route.dest_coords ? `
                <button class="btn btn-secondary" onclick='viewOnMap(${JSON.stringify(route).replace(/'/g, "&apos;")})'>
                    📍 View on Map
                </button>
                ` : ''}
                <button class="btn btn-primary" onclick="bookRoute(${route.id}, '${route.mode}')">
                    Book Now
                </button>
            </div>
        `;
        
        routeResults.appendChild(routeCard);
    });
    
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Book route
async function bookRoute(routeId, mode) {
    const source = document.getElementById('source').value;
    const destination = document.getElementById('destination').value;
    
    // Determine booking type based on mode
    let bookingType = mode;
    if (mode === 'bike' || mode === 'car' || mode === 'walk') {
        bookingType = 'aggregator'; // For demo purposes
    }
    
    const bookingData = {
        booking_type: bookingType,
        source: source,
        destination: destination,
        journey_date: new Date().toISOString().split('T')[0],
        journey_time: '10:00:00',
        passenger_count: 1,
        fare_amount: 50.00
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/bookings/create`, {
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

// My Bookings
const myBookingsLink = document.getElementById('my-bookings-link');
const bookingsModal = document.getElementById('bookings-modal');
const closeModal = document.querySelector('.close');

if (myBookingsLink) {
    myBookingsLink.addEventListener('click', async (e) => {
        e.preventDefault();
        await loadMyBookings();
        bookingsModal.style.display = 'block';
    });
}

if (closeModal) {
    closeModal.addEventListener('click', () => {
        bookingsModal.style.display = 'none';
    });
}

window.addEventListener('click', (e) => {
    if (e.target === bookingsModal) {
        bookingsModal.style.display = 'none';
    }
});

async function loadMyBookings() {
    try {
        const response = await fetch(`${API_BASE_URL}/bookings/my-bookings`, {
            headers: {
                'Authorization': `Bearer ${auth.token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayBookings(data.bookings);
        } else {
            alert(data.message || 'Failed to load bookings');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Network error. Please try again.');
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

// ========== MAP FUNCTIONALITY ==========

let map = null;
let currentRoute = null;
let animationInterval = null;
let trackingId = null;
let currentMarker = null;
let routePolyline = null;

function initializeMap() {
    if (!map) {
        map = L.map('map-container').setView([12.9716, 77.5946], 12); // Default to MG Road, Bangalore
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);
    }
}

function viewOnMap(route) {
    initializeMap();
    
    currentRoute = route;
    
    // Show map section
    document.getElementById('map-section').style.display = 'block';
    document.getElementById('map-section').scrollIntoView({ behavior: 'smooth' });
    
    // Clear previous route
    if (routePolyline) {
        map.removeLayer(routePolyline);
    }
    if (currentMarker) {
        map.removeLayer(currentMarker);
    }
    
    // Add source and destination markers
    const sourceCoords = route.source_coords;
    const destCoords = route.dest_coords;
    
    // Create route polyline
    routePolyline = L.polyline([
        [sourceCoords.lat, sourceCoords.lng],
        [destCoords.lat, destCoords.lng]
    ], {
        color: '#4CAF50',
        weight: 4,
        opacity: 0.7
    }).addTo(map);
    
    // Add destination marker
    L.marker([destCoords.lat, destCoords.lng], {
        icon: L.divIcon({
            className: 'custom-marker',
            html: '🎯',
            iconSize: [30, 30]
        })
    }).addTo(map).bindPopup(`<b>Destination:</b> ${route.destination}`);
    
    // Create moving marker with emoji
    const emoji = getModeEmoji(route.mode);
    currentMarker = L.marker([sourceCoords.lat, sourceCoords.lng], {
        icon: L.divIcon({
            className: 'custom-marker',
            html: emoji,
            iconSize: [40, 40]
        })
    }).addTo(map).bindPopup(`<b>Source:</b> ${route.source}`);
    
    // Fit map to route bounds
    map.fitBounds(routePolyline.getBounds(), { padding: [50, 50] });
    
    // Update navigation info
    updateNavigationInfo({
        position: route.source,
        distance: route.distance_km,
        time: route.duration_mins,
        speed: route.speed_kmh || 0
    });
}

function startNavigation() {
    if (!currentRoute) {
        alert('Please select a route first');
        return;
    }
    
    const startBtn = document.querySelector('.btn-start');
    const stopBtn = document.querySelector('.btn-stop');
    
    startBtn.disabled = true;
    stopBtn.disabled = false;
    
    // Start tracking session
    fetch('/api/navigation/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${auth.token}`
        },
        body: JSON.stringify({
            booking_id: 0,
            vehicle_number: currentRoute.mode.toUpperCase(),
            source: currentRoute.source,
            source_lat: currentRoute.source_coords.lat,
            source_lng: currentRoute.source_coords.lng,
            total_distance: currentRoute.distance_km
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            trackingId = data.tracking_id;
            animateRoute();
        }
    })
    .catch(err => console.error('Error starting navigation:', err));
}

function stopNavigation() {
    const startBtn = document.querySelector('.btn-start');
    const stopBtn = document.querySelector('.btn-stop');
    
    if (animationInterval) {
        clearInterval(animationInterval);
        animationInterval = null;
    }
    
    startBtn.disabled = false;
    stopBtn.disabled = true;
    
    // Stop tracking session
    if (trackingId) {
        fetch('/api/navigation/stop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${auth.token}`
            },
            body: JSON.stringify({ tracking_id: trackingId })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert('Navigation stopped');
            }
        })
        .catch(err => console.error('Error stopping navigation:', err));
    }
}

function closeMap() {
    document.getElementById('map-section').style.display = 'none';
    stopNavigation();
}

function animateRoute() {
    if (!currentRoute || !currentMarker) return;
    
    const start = currentRoute.source_coords;
    const end = currentRoute.dest_coords;
    const duration = currentRoute.duration_mins * 60 * 1000; // Convert to milliseconds
    const updateInterval = 1000; // Update every second
    const totalSteps = duration / updateInterval;
    
    let currentStep = 0;
    
    animationInterval = setInterval(() => {
        currentStep++;
        
        if (currentStep >= totalSteps) {
            clearInterval(animationInterval);
            updateNavigationInfo({
                position: currentRoute.destination,
                distance: 0,
                time: 0,
                speed: 0
            });
            alert('Destination reached!');
            stopNavigation();
            return;
        }
        
        // Calculate current position using linear interpolation
        const progress = currentStep / totalSteps;
        const currentLat = start.lat + (end.lat - start.lat) * progress;
        const currentLng = start.lng + (end.lng - start.lng) * progress;
        
        // Update marker position
        currentMarker.setLatLng([currentLat, currentLng]);
        
        // Calculate remaining distance and time
        const remainingDistance = currentRoute.distance_km * (1 - progress);
        const remainingTime = currentRoute.duration_mins * (1 - progress);
        
        // Update navigation info
        updateNavigationInfo({
            position: `${currentLat.toFixed(4)}, ${currentLng.toFixed(4)}`,
            distance: remainingDistance.toFixed(2),
            time: Math.ceil(remainingTime),
            speed: currentRoute.speed_kmh || 0
        });
        
        // Send position update to backend
        if (trackingId) {
            fetch('/api/navigation/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${auth.token}`
                },
                body: JSON.stringify({
                    tracking_id: trackingId,
                    lat: currentLat,
                    lng: currentLng,
                    distance_remaining: remainingDistance,
                    location: `${currentLat.toFixed(4)}, ${currentLng.toFixed(4)}`
                })
            }).catch(err => console.error('Error updating position:', err));
        }
        
    }, updateInterval);
}

function updateNavigationInfo(info) {
    document.getElementById('current-position').textContent = info.position;
    document.getElementById('distance-remaining').textContent = `${info.distance} km`;
    document.getElementById('time-remaining').textContent = `${info.time} mins`;
    document.getElementById('current-speed').textContent = `${info.speed} km/h`;
}

function getModeEmoji(mode) {
    const emojis = {
        'bike': '🏍️',
        'car': '🚗',
        'walk': '🚶',
        'bus': '🚌',
        'metro': '🚇',
        'auto': '🛺',
        'cab': '🚕',
        'bmtc': '🚌',
        'aggregator': '🚕'
    };
    return emojis[mode.toLowerCase()] || '🚗';
}

// Make functions global for inline onclick
window.openService = openService;
window.bookRoute = bookRoute;
window.viewOnMap = viewOnMap;
window.startNavigation = startNavigation;
window.stopNavigation = stopNavigation;
window.closeMap = closeMap;

