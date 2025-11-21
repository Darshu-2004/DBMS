// Expenses JavaScript
const API_URL = 'http://localhost:5000';
let auth = null;

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

document.getElementById('logout-link')?.addEventListener('click', (e) => {
    e.preventDefault();
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = 'signin.html';
});

// Load expenses on page load
window.addEventListener('DOMContentLoaded', loadExpenses);

async function loadExpenses() {
    try {
        console.log('🔄 Loading expenses...');
        const response = await fetch(`${API_URL}/api/expenses/all`, {
            headers: {
                'Authorization': `Bearer ${auth.token}`
            }
        });
        
        const data = await response.json();
        console.log('📦 Data received:', data);
        
        if (data.success) {
            console.log('✅ Displaying summary cards...');
            displaySummary(data.summary, data.expenses);
            console.log('✅ Displaying expense table...');
            displayExpenses(data.expenses);
            console.log('✅ Displaying monthly breakdown...');
            displayMonthly(data.summary.monthly);
            console.log('✅ Displaying daily breakdown...');
            displayDaily(data.summary.daily);
            console.log('✅ Displaying booking stats...');
            displayBookingStats(data.booking_stats);
            console.log('✅ Loading user daily expenses...');
            loadUserDailyExpenses();
            console.log('🎉 All data loaded successfully!');
        }
    } catch (error) {
        console.error('❌ Error loading expenses:', error);
    }
}

function displaySummary(summary, expenses) {
    // Calculate category breakdown
    const breakdown = {
        KSRTC: { count: 0, total: 0 },
        'Train Ticket': { count: 0, total: 0 },
        FLIGHT: { count: 0, total: 0 }
    };
    
    expenses.forEach(exp => {
        const category = exp.category || 'KSRTC';
        if (!breakdown[category]) {
            breakdown[category] = { count: 0, total: 0 };
        }
        breakdown[category].count++;
        breakdown[category].total += exp.amount;
    });
    
    const container = document.getElementById('summary-cards');
    container.innerHTML = `
        <div class="summary-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <h3>💰 Total Spent</h3>
            <p class="amount">₹${summary.total_spent.toFixed(2)}</p>
            <small style="opacity: 0.8; font-size: 12px;">All categories combined</small>
        </div>
        <div class="summary-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
            <h3>🚌 KSRTC</h3>
            <p class="amount">₹${breakdown.KSRTC.total.toFixed(2)}</p>
            <small style="opacity: 0.8; font-size: 12px;">${breakdown.KSRTC.count} ticket${breakdown.KSRTC.count !== 1 ? 's' : ''}</small>
        </div>
        <div class="summary-card" style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);">
            <h3>🚂 Trains</h3>
            <p class="amount">₹${breakdown['Train Ticket'].total.toFixed(2)}</p>
            <small style="opacity: 0.8; font-size: 12px;">${breakdown['Train Ticket'].count} ticket${breakdown['Train Ticket'].count !== 1 ? 's' : ''}</small>
        </div>
        <div class="summary-card" style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);">
            <h3>✈️ Flights</h3>
            <p class="amount">₹${breakdown.FLIGHT.total.toFixed(2)}</p>
            <small style="opacity: 0.8; font-size: 12px;">${breakdown.FLIGHT.count} ticket${breakdown.FLIGHT.count !== 1 ? 's' : ''}</small>
        </div>
        <div class="summary-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <h3>🎫 Total Tickets</h3>
            <p class="amount">${summary.total_bookings}</p>
            <small style="opacity: 0.8; font-size: 12px;">
                🚌 ${breakdown.KSRTC.count} · 🚂 ${breakdown['Train Ticket'].count} · ✈️ ${breakdown.FLIGHT.count}
            </small>
        </div>
        <div class="summary-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <h3>📊 Average Cost</h3>
            <p class="amount">₹${summary.avg_per_booking.toFixed(2)}</p>
            <small style="opacity: 0.8; font-size: 12px;">Per ticket</small>
        </div>
    `;
}

function displayExpenses(expenses) {
    const tbody = document.getElementById('expense-body');
    
    if (expenses.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;">No expenses found.</td></tr>';
        return;
    }
    
    tbody.innerHTML = expenses.slice(0, 50).map(exp => `
        <tr>
            <td>${formatDate(exp.date)}</td>
            <td><span class="category-badge category-${exp.category}">${exp.category}</span></td>
            <td>${exp.description}</td>
            <td><strong>₹${exp.amount.toFixed(2)}</strong></td>
        </tr>
    `).join('');
}

function displayMonthly(monthly) {
    const container = document.getElementById('monthly-summary');
    
    if (monthly.length === 0) {
        container.innerHTML = '<p>No monthly data available.</p>';
        return;
    }
    
    container.innerHTML = `
        <table style="width:100%">
            <thead>
                <tr>
                    <th>Month</th>
                    <th>Total Amount</th>
                    <th>Bookings</th>
                    <th>Most Used Mode</th>
                    <th>Average</th>
                </tr>
            </thead>
            <tbody>
                ${monthly.map(m => {
                    const modeIcon = m.most_used_mode === 'KSRTC' ? '🚌' : (m.most_used_mode === 'Train' ? '🚂' : '✈️');
                    return `
                    <tr>
                        <td>${formatMonth(m.month)}</td>
                        <td><strong>₹${m.total_amount.toFixed(2)}</strong></td>
                        <td>${m.booking_count} <small>(🚌${m.ksrtc_count} 🚂${m.train_count} ✈️${m.flight_count})</small></td>
                        <td>${modeIcon} ${m.most_used_mode}</td>
                        <td>₹${(m.total_amount / m.booking_count).toFixed(2)}</td>
                    </tr>
                `;
                }).join('')}
            </tbody>
        </table>
    `;
}

function displayBookingStats(stats) {
    const container = document.getElementById('booking-stats');
    if (!container) return;
    
    const total_bookings = stats.ksrtc.total + stats.train.total + stats.flight.total;
    const total_confirmed = stats.ksrtc.confirmed + stats.train.confirmed + stats.flight.confirmed;
    const total_cancelled = stats.ksrtc.cancelled + stats.train.cancelled + stats.flight.cancelled;
    
    container.innerHTML = `
        <h3 style="margin-bottom: 15px;">📊 Booking Statistics</h3>
        <table style="width:100%">
            <thead>
                <tr>
                    <th>Transport Mode</th>
                    <th>Total Bookings</th>
                    <th>✅ Confirmed</th>
                    <th>❌ Cancelled</th>
                    <th>Cancellation Rate</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>🚌 KSRTC</strong></td>
                    <td>${stats.ksrtc.total}</td>
                    <td>${stats.ksrtc.confirmed}</td>
                    <td>${stats.ksrtc.cancelled}</td>
                    <td>${stats.ksrtc.total > 0 ? ((stats.ksrtc.cancelled / stats.ksrtc.total) * 100).toFixed(1) : 0}%</td>
                </tr>
                <tr>
                    <td><strong>🚂 Trains</strong></td>
                    <td>${stats.train.total}</td>
                    <td>${stats.train.confirmed}</td>
                    <td>${stats.train.cancelled}</td>
                    <td>${stats.train.total > 0 ? ((stats.train.cancelled / stats.train.total) * 100).toFixed(1) : 0}%</td>
                </tr>
                <tr>
                    <td><strong>✈️ Flights</strong></td>
                    <td>${stats.flight.total}</td>
                    <td>${stats.flight.confirmed}</td>
                    <td>${stats.flight.cancelled}</td>
                    <td>${stats.flight.total > 0 ? ((stats.flight.cancelled / stats.flight.total) * 100).toFixed(1) : 0}%</td>
                </tr>
                <tr style="background: #f3f4f6; font-weight: bold;">
                    <td>📈 TOTAL</td>
                    <td>${total_bookings}</td>
                    <td>${total_confirmed}</td>
                    <td>${total_cancelled}</td>
                    <td>${total_bookings > 0 ? ((total_cancelled / total_bookings) * 100).toFixed(1) : 0}%</td>
                </tr>
            </tbody>
        </table>
    `;
}

function displayDaily(daily) {
    const container = document.getElementById('daily-summary');
    
    if (!daily || daily.length === 0) {
        container.innerHTML = '<p>No daily data available.</p>';
        return;
    }
    
    container.innerHTML = `
        <table style="width:100%">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Total Spent</th>
                    <th>Bookings</th>
                    <th>Mode Breakdown</th>
                    <th>Most Used</th>
                </tr>
            </thead>
            <tbody>
                ${daily.map(d => {
                    const modeIcon = d.most_used_mode === 'KSRTC' ? '🚌' : (d.most_used_mode === 'Train' ? '🚂' : '✈️');
                    return `
                    <tr>
                        <td><strong>${formatDate(d.date)}</strong></td>
                        <td><strong style="color: #667eea;">₹${d.total_amount.toFixed(2)}</strong></td>
                        <td>${d.booking_count}</td>
                        <td><small>🚌 ${d.ksrtc_count} · 🚂 ${d.train_count} · ✈️ ${d.flight_count}</small></td>
                        <td>${modeIcon} ${d.most_used_mode}</td>
                    </tr>
                `;
                }).join('')}
            </tbody>
        </table>
    `;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-IN', options);
}

function formatMonth(monthString) {
    const [year, month] = monthString.split('-');
    const date = new Date(year, month - 1, 1);
    return date.toLocaleDateString('en-IN', { year: 'numeric', month: 'long' });
}

// Load user's daily expenses
async function loadUserDailyExpenses() {
    const dateInput = document.getElementById('user-expense-date');
    const date = dateInput ? dateInput.value : new Date().toISOString().split('T')[0];
    
    if (!date) {
        console.log('No date selected, using today');
        return;
    }
    
    try {
        console.log('Loading user expenses for date:', date);
        const response = await fetch(`${API_URL}/api/user/expenses/daily?date=${date}`, {
            headers: { 'Authorization': `Bearer ${auth.token}` }
        });
        
        const result = await response.json();
        console.log('User daily expenses response:', result);
        
        if (result.success) {
            displayUserDailyExpenses(result);
        } else {
            console.error('Error from API:', result.message);
        }
    } catch (error) {
        console.error('Error loading daily expenses:', error);
    }
}

function displayUserDailyExpenses(data) {
    const container = document.getElementById('user-daily-expenses');
    if (!container) return;
    
    const formatCurrency = (amount) => `₹${amount.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    
    container.innerHTML = `
        <div style="background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-top: 30px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2 style="margin: 0;">📅 Daily Expense Breakdown</h2>
                <div>
                    <input type="date" id="user-expense-date" value="${data.date}" 
                        style="padding: 10px; border: 1px solid #ddd; border-radius: 8px; margin-right: 10px;">
                    <button onclick="loadUserDailyExpenses()" 
                        style="padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer;">
                        Load
                    </button>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 25px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px;">
                    <div style="font-size: 14px; opacity: 0.9; margin-bottom: 5px;">Total Spent</div>
                    <div style="font-size: 28px; font-weight: bold;">${formatCurrency(data.total_spent)}</div>
                    <div style="font-size: 12px; opacity: 0.8;">${data.total_bookings} bookings</div>
                </div>
                <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; border-radius: 10px;">
                    <div style="font-size: 14px; opacity: 0.9; margin-bottom: 5px;">🚌 KSRTC</div>
                    <div style="font-size: 28px; font-weight: bold;">${formatCurrency(data.ksrtc.total_spent)}</div>
                    <div style="font-size: 12px; opacity: 0.8;">${data.ksrtc.confirmed_bookings} trips</div>
                </div>
                <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 20px; border-radius: 10px;">
                    <div style="font-size: 14px; opacity: 0.9; margin-bottom: 5px;">🚂 Trains</div>
                    <div style="font-size: 28px; font-weight: bold;">${formatCurrency(data.train.total_spent)}</div>
                    <div style="font-size: 12px; opacity: 0.8;">${data.train.confirmed_bookings} trips</div>
                </div>
                <div style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white; padding: 20px; border-radius: 10px;">
                    <div style="font-size: 14px; opacity: 0.9; margin-bottom: 5px;">✈️ Flights</div>
                    <div style="font-size: 28px; font-weight: bold;">${formatCurrency(data.flight.total_spent)}</div>
                    <div style="font-size: 12px; opacity: 0.8;">${data.flight.confirmed_bookings} trips</div>
                </div>
            </div>
            
            ${data.recent_bookings && data.recent_bookings.length > 0 ? `
                <h3 style="margin-top: 25px; margin-bottom: 15px;">Recent Bookings for ${new Date(data.date).toLocaleDateString('en-IN', {year: 'numeric', month: 'long', day: 'numeric'})}</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <thead style="background: #f8f9fa;">
                        <tr>
                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e5e7eb;">Type</th>
                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e5e7eb;">Reference</th>
                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e5e7eb;">Route</th>
                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e5e7eb;">Fare</th>
                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #e5e7eb;">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.recent_bookings.map(booking => {
                            const statusColor = booking.booking_status === 'Confirmed' ? '#10b981' : '#ef4444';
                            const typeIcon = booking.type === 'KSRTC' ? '🚌' : booking.type === 'Train' ? '🚂' : '✈️';
                            return `
                                <tr style="border-bottom: 1px solid #e5e7eb;">
                                    <td style="padding: 12px;">${typeIcon} ${booking.type}</td>
                                    <td style="padding: 12px;"><code>${booking.booking_reference}</code></td>
                                    <td style="padding: 12px;">${booking.source} → ${booking.destination}</td>
                                    <td style="padding: 12px;"><strong>${formatCurrency(booking.total_fare)}</strong></td>
                                    <td style="padding: 12px;"><span style="padding: 4px 12px; background: ${statusColor}20; color: ${statusColor}; border-radius: 12px; font-size: 12px; font-weight: 600;">${booking.booking_status}</span></td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            ` : `
                <div style="text-align: center; padding: 40px; color: #999;">
                    <p style="font-size: 48px; margin: 0;">📭</p>
                    <p style="margin-top: 10px;">No bookings for this date</p>
                </div>
            `}
        </div>
    `;
}

window.loadUserDailyExpenses = loadUserDailyExpenses;
