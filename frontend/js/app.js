// API URLs
const FLASK_API = 'http://localhost:5000';
const FASTAPI_URL = 'http://localhost:8000';

// State management
let sourceLocation = null;
let destinationLocation = null;
let routeData = null;
let navigationMapHtml = null;
let selectedRouteIndex = null;
let navigating = false;

// Auth
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

const sourceInput = document.getElementById('source');
const destInput = document.getElementById('destination');
const sourceSuggestions = document.getElementById('source-suggestions');
const destSuggestions = document.getElementById('destination-suggestions');

let searchTimeout = null;

if (sourceInput) {
    sourceInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const query = e.target.value.trim();
        
        if (query.length < 3) {
            sourceSuggestions.classList.remove('active');
            return;
        }
        
        searchTimeout = setTimeout(() => searchLocation(query, 'source'), 300);
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
        
        searchTimeout = setTimeout(() => searchLocation(query, 'destination'), 300);
    });
}

async function searchLocation(query, type) {
    try {
        console.log(`🔍 Searching for: ${query}`);
        const url = `${FASTAPI_URL}/api/search-location?query=${encodeURIComponent(query + ', Bangalore')}`;
        console.log(`📡 Fetching: ${url}`);
        
        const response = await fetch(url);
        console.log(`✅ Response status: ${response.status}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log(`📦 Data received:`, data);
        
        const suggestionsDiv = type === 'source' ? sourceSuggestions : destSuggestions;
        
        if (data.results && data.results.length > 0) {
            suggestionsDiv.innerHTML = data.results.map(result => `
                <div class="suggestion-item" onclick='selectLocation(${JSON.stringify(result).replace(/'/g, "&#39;")}, "${type}")'>
                    <strong>📍 ${result.display_name.split(',')[0]}</strong>
                    <small>${result.display_name}</small>
                </div>
            `).join('');
            suggestionsDiv.classList.add('active');
            console.log(`✅ Showing ${data.results.length} suggestions`);
        } else {
            suggestionsDiv.classList.remove('active');
            console.log(`⚠️ No results found`);
        }
    } catch (error) {
        console.error('❌ Location search error:', error);
        alert(`Location search failed: ${error.message}\n\nMake sure the FastAPI server is running on port 8001`);
    }
}

function selectLocation(location, type) {
    if (type === 'source') {
        sourceLocation = location;
        sourceInput.value = location.display_name.split(',').slice(0, 2).join(', ');
        sourceSuggestions.classList.remove('active');
    } else {
        destinationLocation = location;
        destInput.value = location.display_name.split(',').slice(0, 2).join(', ');
        destSuggestions.classList.remove('active');
    }
}

// Close suggestions
document.addEventListener('click', (e) => {
    if (!e.target.closest('.form-group')) {
        sourceSuggestions.classList.remove('active');
        destSuggestions.classList.remove('active');
    }
});

// ========== ROUTE OPTIMIZATION ==========

const searchForm = document.getElementById('route-search-form');
if (searchForm) {
    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!sourceLocation || !destinationLocation) {
            alert('Please select source and destination from the dropdown suggestions');
            return;
        }
        
        await optimizeRoute();
    });
}

async function optimizeRoute() {
    try {
        // Show loading
        const resultsSection = document.getElementById('results-section');
        const routeResults = document.getElementById('route-results');
        routeResults.innerHTML = '<div class="loading">🔄 Finding best routes...</div>';
        resultsSection.style.display = 'block';
        
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
            routeData = data;
            displayRoutes(data);
        } else {
            alert('No routes found');
        }
    } catch (error) {
        console.error('Route optimization error:', error);
        alert('Error finding routes. Make sure FastAPI is running on port 8000');
    }
}

function displayRoutes(data) {
    const resultsSection = document.getElementById('results-section');
    const routeResults = document.getElementById('route-results');
    
    if (!resultsSection || !routeResults) return;
    
    routeResults.innerHTML = '';
    
    // Hide map section
    document.getElementById('map-section').style.display = 'none';
    
    // Display each route
    data.metrics.forEach((metric, index) => {
        const routeCard = document.createElement('div');
        routeCard.className = 'route-card';
        
        const incidents = data.incidents[index] || [];
        
        routeCard.innerHTML = `
            <div class="route-header">
                <div class="route-mode">
                    🚗 Route ${index + 1}
                </div>
                <button class="btn btn-primary btn-start-nav" onclick="startNavigation(${index})">
                    ▶️ Start Navigation
                </button>
            </div>
            <div class="route-details">
                <div class="route-detail">
                    <strong>⏱️ Time</strong>
                    <span>${(metric.time_mins || metric.time_minutes || 0).toFixed(0)} mins</span>
                </div>
                <div class="route-detail">
                    <strong>📏 Distance</strong>
                    <span>${(metric.distance_km || 0).toFixed(2)} km</span>
                </div>
                <div class="route-detail">
                    <strong>🚀 Avg Speed</strong>
                    <span>${(metric.avg_speed_kmh || 0).toFixed(1)} km/h</span>
                </div>
                <div class="route-detail">
                    <strong>⛽ Fuel Cost</strong>
                    <span>₹${(metric.fuel_rupees || metric.cost_rupees || 0).toFixed(2)}</span>
                </div>
                <div class="route-detail">
                    <strong>⚠️ Incidents</strong>
                    <span class="${incidents.length > 0 ? 'text-danger' : ''}">${incidents.length}</span>
                </div>
            </div>
            ${incidents.length > 0 ? `
            <div class="incidents-list">
                <strong>⚠️ Traffic Incidents:</strong>
                ${incidents.slice(0, 3).map(inc => `
                    <div class="incident-badge">${inc.type || inc.severity || 'Traffic'}</div>
                `).join('')}
                ${incidents.length > 3 ? `<div class="incident-badge">+${incidents.length - 3} more</div>` : ''}
            </div>
            ` : ''}
        `;
        
        routeResults.appendChild(routeCard);
    });
    
    // Show all routes preview map
    const previewCard = document.createElement('div');
    previewCard.className = 'route-card map-preview-card';
    previewCard.innerHTML = `
        <div class="route-header">
            <h3>🗺️ All Routes Preview</h3>
        </div>
        <div class="map-preview-container">
            <iframe srcdoc="${escapeHtml(data.map_html)}" style="width:100%; height:500px; border:none; border-radius:8px;"></iframe>
        </div>
        <p class="text-muted" style="margin-top:1rem; font-size:0.9rem;">
            💡 Click "Start Navigation" on any route to see detailed navigation with moving car emoji
        </p>
    `;
    routeResults.appendChild(previewCard);
    
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// ========== START NAVIGATION ==========

async function startNavigation(routeIndex) {
    try {
        selectedRouteIndex = routeIndex;
        const selectedRouteNodes = routeData.routes[routeIndex];
        
        // Show loading
        const mapSection = document.getElementById('map-section');
        const mapContainer = document.getElementById('map-container');
        mapContainer.innerHTML = '<div class="loading">🚗 Starting navigation...</div>';
        mapSection.style.display = 'block';
        mapSection.scrollIntoView({ behavior: 'smooth' });
        
        const response = await fetch(`${FASTAPI_URL}/api/start-navigation`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: 'user_' + Date.now(),
                route_id: routeIndex,
                selected_route: selectedRouteNodes,
                src_lat: sourceLocation.lat,
                src_lon: sourceLocation.lon,
                dst_lat: destinationLocation.lat,
                dst_lon: destinationLocation.lon
            })
        });
        
        const data = await response.json();
        
        if (data.map_html) {
            navigationMapHtml = data.map_html;
            navigating = true;
            displayNavigationView();
        } else {
            alert('Failed to start navigation');
        }
        
    } catch (error) {
        console.error('Navigation error:', error);
        alert('Failed to start navigation: ' + error.message);
    }
}

function displayNavigationView() {
    const mapSection = document.getElementById('map-section');
    const mapContainer = document.getElementById('map-container');
    
    // Update map section header
    const mapHeader = mapSection.querySelector('.map-header h2');
    if (mapHeader) {
        mapHeader.innerHTML = `🚗 Navigating Route ${selectedRouteIndex + 1} <span style="margin-left:1rem; font-size:0.9rem; background:#10b981; padding:0.25rem 0.75rem; border-radius:12px;">🟢 Active</span>`;
    }
    
    // Display navigation map
    mapContainer.innerHTML = `
        <iframe srcdoc="${escapeHtml(navigationMapHtml)}" style="width:100%; height:100%; border:none;"></iframe>
    `;
    
    // Update navigation info
    const metric = routeData.metrics[selectedRouteIndex];
    document.getElementById('current-position').textContent = 'Starting...';
    document.getElementById('distance-remaining').textContent = `${(metric.distance_km || 0).toFixed(2)} km`;
    document.getElementById('time-remaining').textContent = `${(metric.time_mins || metric.time_minutes || 0).toFixed(0)} mins`;
    document.getElementById('current-speed').textContent = `${(metric.avg_speed_kmh || 0).toFixed(1)} km/h`;
    
    // Show stop button, hide start button
    const startBtn = document.querySelector('.btn-start');
    const stopBtn = document.querySelector('.btn-stop');
    if (startBtn) startBtn.style.display = 'none';
    if (stopBtn) stopBtn.style.display = 'block';
    
    // Scroll to map
    mapSection.scrollIntoView({ behavior: 'smooth' });
}

function stopNavigation() {
    navigating = false;
    navigationMapHtml = null;
    
    // Show start button, hide stop button
    const startBtn = document.querySelector('.btn-start');
    const stopBtn = document.querySelector('.btn-stop');
    if (startBtn) startBtn.style.display = 'block';
    if (stopBtn) stopBtn.style.display = 'none';
    
    // Clear map
    const mapContainer = document.getElementById('map-container');
    if (mapContainer) {
        mapContainer.innerHTML = '<p style="padding:2rem; text-align:center; color:#6b7280;">Navigation stopped. Select a route to start again.</p>';
    }
}

function closeMap() {
    stopNavigation();
    document.getElementById('map-section').style.display = 'none';
}

// ========== MY BOOKINGS (PUBLIC TRANSPORT ONLY) ==========

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

// Service cards
function openService(serviceType) {
    alert(`${serviceType.toUpperCase()} booking feature coming soon!`);
}

// Coming soon alert
function showComingSoon(feature) {
    alert(`${feature} feature is coming soon! Stay tuned for updates.`);
}

// Make functions global
window.openService = openService;
window.showComingSoon = showComingSoon;
window.selectLocation = selectLocation;
window.startNavigation = startNavigation;
window.stopNavigation = stopNavigation;
window.closeMap = closeMap;
