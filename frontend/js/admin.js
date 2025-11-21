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
    const adminNameElement = document.getElementById('admin-name');
    if (adminNameElement) {
        adminNameElement.textContent = `Hello, ${auth.user.full_name || auth.user.username}`;
    }
    
    // Load dashboard data
    loadDashboard();
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

// Load complete dashboard
async function loadDashboard() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/dashboard`, {
            headers: {
                'Authorization': `Bearer ${auth.token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            const dashboard = data.dashboard;
            
            // Update overview stats
            updateOverviewStats(dashboard);
            
            // Update all sections
            updateTransportModeStats(dashboard.transport_modes);
            updatePrivateModeStats(dashboard.private_mode);
            updatePublicModeStats(dashboard.public_mode);
            updateMultiModalStats(dashboard.multi_modal);
            updateOptimizationStats(dashboard.optimization);
            updatePopularRoutes(dashboard.popular_routes);
            updateBookingStats(dashboard.bookings);
            updateUserActivity(dashboard.user_activity);
        } else {
            console.error('Failed to load dashboard:', data.message);
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Update overview statistics
function updateOverviewStats(dashboard) {
    // Calculate total searches
    const totalSearches = dashboard.transport_modes.reduce((sum, mode) => sum + mode.search_count, 0);
    document.getElementById('total-searches').textContent = totalSearches;
    
    // Calculate total bookings from booking system
    const allBookings = dashboard.all_bookings || [];
    const totalBookings = allBookings.reduce((sum, type) => sum + (type.total_bookings || 0), 0);
    document.getElementById('total-bookings').textContent = totalBookings;
    
    // Calculate total revenue
    const totalRevenue = allBookings.reduce((sum, type) => sum + (type.total_revenue || 0), 0);
    document.getElementById('total-revenue').textContent = `₹${totalRevenue.toLocaleString()}`;
    
    // Calculate active users
    const activeUsers = dashboard.user_activity.length;
    document.getElementById('active-users').textContent = activeUsers;
    
    // Update booking system stats
    updateAllBookingStats(allBookings);
    updatePopularRoutesByType(dashboard);
    updateUserExpenses(dashboard.user_expenses || []);
}

// Update transport mode statistics
function updateTransportModeStats(stats) {
    const tbody = document.getElementById('transport-mode-stats');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    stats.forEach(stat => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${stat.transport_mode}</td>
            <td>${stat.search_count}</td>
            <td>${stat.percentage}%</td>
        `;
        tbody.appendChild(row);
    });
}

// Update private mode statistics
function updatePrivateModeStats(stats) {
    const tbody = document.getElementById('private-mode-stats');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (stats.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3">No data available</td></tr>';
        return;
    }
    
    stats.forEach(stat => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${stat.private_mode || 'N/A'}</td>
            <td>${stat.usage_count}</td>
            <td>${stat.percentage}%</td>
        `;
        tbody.appendChild(row);
    });
}

// Update public mode statistics
function updatePublicModeStats(stats) {
    const tbody = document.getElementById('public-mode-stats');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (stats.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3">No data available</td></tr>';
        return;
    }
    
    stats.forEach(stat => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${stat.public_mode || 'N/A'}</td>
            <td>${stat.usage_count}</td>
            <td>${stat.percentage}%</td>
        `;
        tbody.appendChild(row);
    });
}

// Update multi-modal statistics
function updateMultiModalStats(stats) {
    const tbody = document.getElementById('multi-modal-stats');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (stats.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3">No data available</td></tr>';
        return;
    }
    
    stats.forEach(stat => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${stat.multi_modal_type || 'N/A'}</td>
            <td>${stat.usage_count}</td>
            <td>${stat.percentage}%</td>
        `;
        tbody.appendChild(row);
    });
}

// Update optimization preferences
function updateOptimizationStats(stats) {
    const tbody = document.getElementById('optimization-stats');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (stats.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3">No data available</td></tr>';
        return;
    }
    
    stats.forEach(stat => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${stat.preference_type}</td>
            <td>${stat.preference_count}</td>
            <td>${stat.percentage}%</td>
        `;
        tbody.appendChild(row);
    });
}

// Update popular routes
function updatePopularRoutes(routes) {
    const tbody = document.getElementById('popular-routes');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (routes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4">No data available</td></tr>';
        return;
    }
    
    routes.forEach(route => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${route.source_location}</td>
            <td>${route.destination_location}</td>
            <td>${route.transport_mode}</td>
            <td>${route.search_count}</td>
        `;
        tbody.appendChild(row);
    });
}

// Update booking statistics
function updateBookingStats(stats) {
    const tbody = document.getElementById('booking-stats');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (stats.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5">No data available</td></tr>';
        return;
    }
    
    stats.forEach(stat => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${stat.booking_type}</td>
            <td>${stat.total_bookings}</td>
            <td>${stat.confirmed_bookings}</td>
            <td>${stat.cancelled_bookings}</td>
            <td>₹${stat.avg_fare || 'N/A'}</td>
        `;
        tbody.appendChild(row);
    });
}

// Update user activity
function updateUserActivity(users) {
    const tbody = document.getElementById('user-activity');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5">No data available</td></tr>';
        return;
    }
    
    users.forEach(user => {
        const row = document.createElement('tr');
        const lastSearch = user.last_search_date ? new Date(user.last_search_date).toLocaleDateString() : 'Never';
        row.innerHTML = `
            <td>${user.username}</td>
            <td>${user.full_name}</td>
            <td>${user.total_searches || 0}</td>
            <td>${user.total_bookings || 0}</td>
            <td>${lastSearch}</td>
        `;
        tbody.appendChild(row);
    });
}

// NEW: Update all booking statistics
function updateAllBookingStats(stats) {
    const tbody = document.getElementById('all-booking-stats');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (stats.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7">No bookings yet</td></tr>';
        return;
    }
    
    stats.forEach(stat => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${stat.transport_type}</strong></td>
            <td>${stat.total_bookings || 0}</td>
            <td>${stat.confirmed_bookings || 0}</td>
            <td>${stat.cancelled_bookings || 0}</td>
            <td>₹${stat.avg_fare || 0}</td>
            <td>₹${(stat.total_revenue || 0).toLocaleString()}</td>
            <td>${stat.unique_users || 0}</td>
        `;
        tbody.appendChild(row);
    });
}

// NEW: Update popular routes by transport type
function updatePopularRoutesByType(dashboard) {
    // KSRTC routes
    const ksrtcTbody = document.getElementById('popular-ksrtc-routes');
    if (ksrtcTbody) {
        ksrtcTbody.innerHTML = '';
        const ksrtcRoutes = dashboard.popular_ksrtc_routes || [];
        if (ksrtcRoutes.length === 0) {
            ksrtcTbody.innerHTML = '<tr><td colspan="3">No data</td></tr>';
        } else {
            ksrtcRoutes.slice(0, 5).forEach(route => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${route.boarding_stop} → ${route.destination_stop}</td>
                    <td>${route.booking_count}</td>
                    <td>₹${route.total_revenue}</td>
                `;
                ksrtcTbody.appendChild(row);
            });
        }
    }
    
    // Train routes
    const trainTbody = document.getElementById('popular-train-routes');
    if (trainTbody) {
        trainTbody.innerHTML = '';
        const trainRoutes = dashboard.popular_train_routes || [];
        if (trainRoutes.length === 0) {
            trainTbody.innerHTML = '<tr><td colspan="3">No data</td></tr>';
        } else {
            trainRoutes.slice(0, 5).forEach(route => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${route.from_station} → ${route.to_station}</td>
                    <td>${route.booking_count}</td>
                    <td>₹${route.total_revenue}</td>
                `;
                trainTbody.appendChild(row);
            });
        }
    }
    
    // Flight routes
    const flightTbody = document.getElementById('popular-flight-routes');
    if (flightTbody) {
        flightTbody.innerHTML = '';
        const flightRoutes = dashboard.popular_flight_routes || [];
        if (flightRoutes.length === 0) {
            flightTbody.innerHTML = '<tr><td colspan="3">No data</td></tr>';
        } else {
            flightRoutes.slice(0, 5).forEach(route => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${route.from_airport} → ${route.to_airport}</td>
                    <td>${route.booking_count}</td>
                    <td>₹${route.total_revenue}</td>
                `;
                flightTbody.appendChild(row);
            });
        }
    }
}

// NEW: Update user expenses
function updateUserExpenses(expenses) {
    const tbody = document.getElementById('user-expenses');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (expenses.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6">No expense data</td></tr>';
        return;
    }
    
    expenses.slice(0, 10).forEach(user => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.username}</td>
            <td>${user.full_name}</td>
            <td><strong>₹${(user.total_expenses || 0).toLocaleString()}</strong></td>
            <td>${user.ksrtc_bookings || 0}</td>
            <td>${user.train_bookings || 0}</td>
            <td>${user.flight_bookings || 0}</td>
        `;
        tbody.appendChild(row);
    });
}
