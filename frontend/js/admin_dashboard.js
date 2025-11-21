// Admin Dashboard JavaScript
const API_URL = 'http://localhost:5000';
let auth = null;
let allData = {};
let charts = {};

// Authentication check - ADMIN ONLY
function checkAuth() {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    if (!token) {
        alert('Please login first!');
        window.location.href = 'signin.html';
        return null;
    }
    
    // Check if user is admin
    if (user.user_type !== 'admin') {
        alert('Access Denied! Admin privileges required.');
        window.location.href = 'index.html';
        return null;
    }
    
    return { token, user };
}

auth = checkAuth();
if (auth && document.getElementById('admin-name')) {
    document.getElementById('admin-name').textContent = `Admin: ${auth.user.full_name || auth.user.username}`;
}

document.getElementById('logout-link')?.addEventListener('click', (e) => {
    e.preventDefault();
    localStorage.clear();
    window.location.href = 'signin.html';
});

// Load all dashboard data
async function loadDashboard() {
    try {
        const response = await fetch(`${API_URL}/api/admin/dashboard`, {
            headers: { 'Authorization': `Bearer ${auth.token}` }
        });
        
        const result = await response.json();
        
        if (result.success) {
            allData = result.dashboard;
            updateKPIs(allData);
            createCharts(allData);
            populateTables(allData);
            calculateSeatStats();
        } else {
            alert('Error loading dashboard: ' + result.message);
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
        alert('Failed to load dashboard data');
    }
}

// Update Key Performance Indicators
function updateKPIs(data) {
    // Get booking stats from all_bookings array
    const bookingStats = data.all_bookings || [];
    let totalBookings = 0;
    let totalRevenue = 0;
    
    bookingStats.forEach(stat => {
        const bookings = parseInt(stat.total_bookings) || 0;
        const revenue = parseFloat(stat.total_revenue) || 0;
        totalBookings += bookings;
        totalRevenue += revenue;
    });
    
    const avgBooking = totalBookings > 0 ? (totalRevenue / totalBookings) : 0;
    const totalUsers = (data.user_activity?.length || 0);
    
    document.getElementById('total-bookings').textContent = totalBookings.toLocaleString();
    document.getElementById('total-users').textContent = totalUsers.toLocaleString();
    document.getElementById('total-revenue').textContent = `₹${totalRevenue.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    document.getElementById('avg-booking').textContent = `₹${avgBooking.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
}

// Create all charts
function createCharts(data) {
    createModeChart(data);
    createRevenueChart(data);
    createTrendChart(data);
    createSeatCharts();
    createPeakHoursChart(data);
}

// Bookings by Mode Chart (Doughnut)
function createModeChart(data) {
    const ctx = document.getElementById('modeChart').getContext('2d');
    
    if (charts.modeChart) charts.modeChart.destroy();
    
    const bookingStats = data.all_bookings || [];
    let ksrtcBookings = 0, trainBookings = 0, flightBookings = 0;
    
    bookingStats.forEach(stat => {
        if (stat.transport_type === 'KSRTC' || stat.booking_type === 'KSRTC') {
            ksrtcBookings = stat.total_bookings || 0;
        } else if (stat.transport_type === 'Train' || stat.booking_type === 'Train') {
            trainBookings = stat.total_bookings || 0;
        } else if (stat.transport_type === 'Flight' || stat.booking_type === 'Flight') {
            flightBookings = stat.total_bookings || 0;
        }
    });
    
    charts.modeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['🚌 KSRTC', '🚂 Trains', '✈️ Flights'],
            datasets: [{
                data: [ksrtcBookings, trainBookings, flightBookings],
                backgroundColor: ['#10b981', '#3b82f6', '#8b5cf6'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

// Revenue Chart (Bar)
function createRevenueChart(data) {
    const ctx = document.getElementById('revenueChart').getContext('2d');
    
    if (charts.revenueChart) charts.revenueChart.destroy();
    
    const bookingStats = data.all_bookings || [];
    let ksrtcRevenue = 0, trainRevenue = 0, flightRevenue = 0;
    
    bookingStats.forEach(stat => {
        if (stat.transport_type === 'KSRTC' || stat.booking_type === 'KSRTC') {
            ksrtcRevenue = stat.total_revenue || 0;
        } else if (stat.transport_type === 'Train' || stat.booking_type === 'Train') {
            trainRevenue = stat.total_revenue || 0;
        } else if (stat.transport_type === 'Flight' || stat.booking_type === 'Flight') {
            flightRevenue = stat.total_revenue || 0;
        }
    });
    
    charts.revenueChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['KSRTC', 'Trains', 'Flights'],
            datasets: [{
                label: 'Revenue (₹)',
                data: [ksrtcRevenue, trainRevenue, flightRevenue],
                backgroundColor: ['#10b981', '#3b82f6', '#8b5cf6']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// Daily Trend Chart (Line)
function createTrendChart(data) {
    const ctx = document.getElementById('trendChart').getContext('2d');
    
    if (charts.trendChart) charts.trendChart.destroy();
    
    const trends = data.daily_trends || [];
    const labels = trends.map(t => {
        // Handle different date formats from MySQL
        let dateStr = t.booking_date || t.date || t.journey_date;
        if (!dateStr) return 'N/A';
        
        // Parse MySQL date format (YYYY-MM-DD)
        const parts = dateStr.split('T')[0].split('-');
        if (parts.length === 3) {
            const date = new Date(parts[0], parts[1] - 1, parts[2]);
            return date.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' });
        }
        return dateStr;
    });
    
    charts.trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'KSRTC',
                    data: trends.map(t => t.ksrtc_bookings || 0),
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Trains',
                    data: trends.map(t => t.train_bookings || 0),
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Flights',
                    data: trends.map(t => t.flight_bookings || 0),
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

// Seat Charts for each transport mode
function createSeatCharts() {
    createSeatChart('ksrtcSeatsChart', 'KSRTC');
    createSeatChart('trainSeatsChart', 'Train');
    createSeatChart('flightSeatsChart', 'Flight');
}

function createSeatChart(canvasId, mode) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    if (charts[canvasId]) charts[canvasId].destroy();
    
    charts[canvasId] = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Booked', 'Available'],
            datasets: [{
                data: [0, 100], // Will be updated with real data
                backgroundColor: ['#ef4444', '#10b981']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

// Peak Hours Chart
function createPeakHoursChart(data) {
    const ctx = document.getElementById('peakHoursChart');
    if (!ctx) return;
    
    if (charts.peakHoursChart) charts.peakHoursChart.destroy();
    
    const peakData = data.peak_hours || [];
    
    // If no data, create a default chart
    if (peakData.length === 0) {
        const hours = Array.from({length: 24}, (_, i) => i);
        charts.peakHoursChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: hours.map(h => `${h}:00`),
                datasets: [{
                    label: 'Bookings',
                    data: new Array(24).fill(0),
                    backgroundColor: '#667eea'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
        return;
    }
    
    charts.peakHoursChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: peakData.map(p => `${p.booking_hour || p.hour || 0}:00`),
            datasets: [{
                label: 'Bookings',
                data: peakData.map(p => p.booking_count || p.total_bookings || 0),
                backgroundColor: '#667eea'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

// Calculate and update seat statistics
async function calculateSeatStats() {
    try {
        // KSRTC Seats
        const ksrtcSeats = await fetch(`${API_URL}/api/admin/seat-stats/ksrtc`, {
            headers: { 'Authorization': `Bearer ${auth.token}` }
        }).then(r => r.json());
        
        if (ksrtcSeats.success) {
            updateSeatChart('ksrtcSeatsChart', ksrtcSeats.data);
            document.getElementById('ksrtc-stats').innerHTML = `
                <strong>Total Seats:</strong> ${ksrtcSeats.data.total}<br>
                <strong>Booked:</strong> ${ksrtcSeats.data.booked} (${ksrtcSeats.data.booked_percent}%)<br>
                <strong>Available:</strong> ${ksrtcSeats.data.available} (${ksrtcSeats.data.available_percent}%)
            `;
        }
        
        // Train Berths
        const trainSeats = await fetch(`${API_URL}/api/admin/seat-stats/train`, {
            headers: { 'Authorization': `Bearer ${auth.token}` }
        }).then(r => r.json());
        
        if (trainSeats.success) {
            updateSeatChart('trainSeatsChart', trainSeats.data);
            document.getElementById('train-stats').innerHTML = `
                <strong>Total Berths:</strong> ${trainSeats.data.total}<br>
                <strong>Booked:</strong> ${trainSeats.data.booked} (${trainSeats.data.booked_percent}%)<br>
                <strong>Available:</strong> ${trainSeats.data.available} (${trainSeats.data.available_percent}%)
            `;
        }
        
        // Flight Seats
        const flightSeats = await fetch(`${API_URL}/api/admin/seat-stats/flight`, {
            headers: { 'Authorization': `Bearer ${auth.token}` }
        }).then(r => r.json());
        
        if (flightSeats.success) {
            updateSeatChart('flightSeatsChart', flightSeats.data);
            document.getElementById('flight-stats').innerHTML = `
                <strong>Total Seats:</strong> ${flightSeats.data.total}<br>
                <strong>Booked:</strong> ${flightSeats.data.booked} (${flightSeats.data.booked_percent}%)<br>
                <strong>Available:</strong> ${flightSeats.data.available} (${flightSeats.data.available_percent}%)
            `;
        }
    } catch (error) {
        console.error('Error loading seat stats:', error);
    }
}

function updateSeatChart(chartId, data) {
    if (charts[chartId]) {
        charts[chartId].data.datasets[0].data = [data.booked, data.available];
        charts[chartId].update();
    }
}

// Populate data tables
function populateTables(data) {
    populatePopularRoutes(data);
    populateUserActivity(data);
    populatePerformanceStats(data);
}

// Popular Routes Table
function populatePopularRoutes(data) {
    const tbody = document.getElementById('popular-routes');
    const routes = [
        ...(data.popular_ksrtc || []).map(r => ({...r, type: '🚌 KSRTC'})),
        ...(data.popular_trains || []).map(r => ({...r, type: '🚂 Train'})),
        ...(data.popular_flights || []).map(r => ({...r, type: '✈️ Flight'}))
    ].sort((a, b) => b.total_bookings - a.total_bookings).slice(0, 10);
    
    tbody.innerHTML = routes.map((route, index) => `
        <tr>
            <td><strong>${index + 1}</strong></td>
            <td>${route.from_location} → ${route.to_location}</td>
            <td>${route.type}</td>
            <td>${route.total_bookings}</td>
            <td>₹${parseFloat(route.total_revenue).toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
            <td>₹${parseFloat(route.avg_fare).toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
            <td><span class="badge badge-success">Active</span></td>
        </tr>
    `).join('');
}

// User Activity Table
function populateUserActivity(data) {
    const tbody = document.getElementById('user-activity');
    const users = data.user_expenses || [];
    
    tbody.innerHTML = users.map(user => `
        <tr>
            <td><strong>${user.username}</strong><br><small>${user.full_name}</small></td>
            <td>${user.ksrtc_bookings + user.train_bookings + user.flight_bookings}</td>
            <td>${user.ksrtc_bookings}</td>
            <td>${user.train_bookings}</td>
            <td>${user.flight_bookings}</td>
            <td><strong>₹${parseFloat(user.total_expenses).toLocaleString('en-IN', {minimumFractionDigits: 2})}</strong></td>
            <td>${new Date().toLocaleDateString()}</td>
        </tr>
    `).join('');
}

// Performance Stats Table
function populatePerformanceStats(data) {
    const tbody = document.getElementById('performance-stats');
    
    const bookingStats = data.all_bookings || [];
    const stats = bookingStats.map(stat => ({
        name: stat.transport_type === 'KSRTC' ? '🚌 KSRTC' : 
              stat.transport_type === 'Train' ? '🚂 Trains' :
              stat.transport_type === 'Flight' ? '✈️ Flights' : '📊 ' + stat.booking_type,
        bookings: stat.total_bookings || 0,
        confirmed: stat.confirmed_bookings || 0,
        cancelled: stat.cancelled_bookings || 0,
        revenue: stat.total_revenue || 0,
        avg_fare: stat.avg_fare || 0
    }));
    
    tbody.innerHTML = stats.map(stat => {
        const cancelRate = stat.bookings > 0 ? ((stat.cancelled / stat.bookings) * 100).toFixed(1) : 0;
        return `
            <tr>
                <td><strong>${stat.name}</strong></td>
                <td>${stat.bookings}</td>
                <td><span class="badge badge-success">${stat.confirmed}</span></td>
                <td><span class="badge badge-danger">${stat.cancelled}</span></td>
                <td>${cancelRate}%</td>
                <td><strong>₹${parseFloat(stat.revenue).toLocaleString('en-IN', {minimumFractionDigits: 2})}</strong></td>
                <td>₹${parseFloat(stat.avg_fare).toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
            </tr>
        `;
    }).join('');
}

// Filter trend chart
function filterTrend(mode) {
    // Update active button
    document.querySelectorAll('.filter-tab').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    // Update chart visibility
    const chart = charts.trendChart;
    if (!chart) return;
    
    chart.data.datasets.forEach((dataset, index) => {
        if (mode === 'all') {
            dataset.hidden = false;
        } else {
            const datasetMode = dataset.label.toLowerCase();
            dataset.hidden = !datasetMode.includes(mode);
        }
    });
    
    chart.update();
}

// Make filterTrend globally accessible
window.filterTrend = filterTrend;

// Load daily revenue data
async function loadDailyRevenue() {
    const dateInput = document.getElementById('revenue-date');
    if (!dateInput) {
        console.error('Date input not found');
        return;
    }
    
    const date = dateInput.value;
    
    if (!date) {
        alert('Please select a date');
        return;
    }
    
    try {
        console.log('Loading revenue for date:', date);
        const response = await fetch(`${API_URL}/api/admin/revenue/daily?date=${date}`, {
            headers: { 'Authorization': `Bearer ${auth.token}` }
        });
        
        const result = await response.json();
        console.log('Daily revenue response:', result);
        
        if (result.success) {
            displayDailyRevenue(result);
        } else {
            console.error('Error from API:', result.message);
            alert('Error loading daily revenue: ' + result.message);
        }
    } catch (error) {
        console.error('Error loading daily revenue:', error);
        alert('Failed to load daily revenue data');
    }
}

function displayDailyRevenue(data) {
    // Update total revenue
    document.getElementById('daily-total-revenue').textContent = `₹${data.total_revenue.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    document.getElementById('daily-total-bookings').textContent = `${data.total_bookings} bookings`;
    
    // Update KSRTC revenue
    document.getElementById('daily-ksrtc-revenue').textContent = `₹${data.ksrtc.total_revenue.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    document.getElementById('daily-ksrtc-bookings').textContent = `${data.ksrtc.confirmed_bookings} bookings (${data.ksrtc.cancelled_bookings} cancelled)`;
    
    // Update Train revenue
    document.getElementById('daily-train-revenue').textContent = `₹${data.train.total_revenue.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    document.getElementById('daily-train-bookings').textContent = `${data.train.confirmed_bookings} bookings (${data.train.cancelled_bookings} cancelled)`;
    
    // Update Flight revenue
    document.getElementById('daily-flight-revenue').textContent = `₹${data.flight.total_revenue.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    document.getElementById('daily-flight-bookings').textContent = `${data.flight.confirmed_bookings} bookings (${data.flight.cancelled_bookings} cancelled)`;
    
    // Update top spenders table
    const topSpendersTable = document.getElementById('top-spenders-table');
    if (data.top_users && data.top_users.length > 0) {
        topSpendersTable.innerHTML = data.top_users.map((user, index) => {
            const avgPerBooking = user.total_spent / user.total_bookings;
            return `
                <tr>
                    <td><strong>#${index + 1}</strong></td>
                    <td>${user.username}</td>
                    <td>${user.email}</td>
                    <td><strong>₹${user.total_spent.toLocaleString('en-IN', {minimumFractionDigits: 2})}</strong></td>
                    <td>${user.total_bookings}</td>
                    <td>₹${avgPerBooking.toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
                </tr>
            `;
        }).join('');
    } else {
        topSpendersTable.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 20px;">No bookings for this date</td></tr>';
    }
}

// Set today's date as default
document.addEventListener('DOMContentLoaded', () => {
    const today = new Date().toISOString().split('T')[0];
    const dateInput = document.getElementById('revenue-date');
    if (dateInput) {
        dateInput.value = today;
        // Auto-load today's revenue after a short delay to ensure dashboard is loaded
        setTimeout(() => {
            loadDailyRevenue();
        }, 1000);
    }
});

window.loadDailyRevenue = loadDailyRevenue;

// Load dashboard on page load
window.addEventListener('DOMContentLoaded', loadDashboard);
