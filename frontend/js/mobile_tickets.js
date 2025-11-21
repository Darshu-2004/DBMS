// Mobile Tickets JavaScript
const API_URL = 'http://localhost:5000';
let auth = null;
let allTickets = [];

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

// Load tickets on page load
window.addEventListener('DOMContentLoaded', loadTickets);

async function loadTickets() {
    try {
        const response = await fetch(`${API_URL}/api/tickets/all`, {
            headers: {
                'Authorization': `Bearer ${auth.token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            allTickets = data.tickets;
            displayTickets(allTickets);
            
            // Update filter counts
            document.querySelector('[data-filter="all"]').textContent = `All Tickets (${data.count.total})`;
            document.querySelector('[data-filter="active"]').textContent = `Active (${data.count.active})`;
            document.querySelector('[data-filter="expired"]').textContent = `Expired (${data.count.expired})`;
            document.querySelector('[data-filter="cancelled"]').textContent = `Cancelled (${data.count.cancelled})`;
        }
    } catch (error) {
        console.error('Error loading tickets:', error);
    }
}

function displayTickets(tickets) {
    const container = document.getElementById('tickets-container');
    
    if (tickets.length === 0) {
        container.innerHTML = '<div class="no-tickets"><p>📭 No tickets found. <br><a href="ksrtc.html">Book KSRTC</a> | <a href="/trains">Book Train</a> | <a href="/flights">Book Flight</a></p></div>';
        return;
    }
    
    container.innerHTML = tickets.map(ticket => createTicketCard(ticket)).join('');
    
    // Generate QR codes
    tickets.forEach(ticket => {
        if (ticket.ticket_number && !ticket.is_expired && ticket.booking_status === 'Confirmed') {
            generateQRCode(ticket.ticket_number, ticket.booking_reference || ticket.pnr || ticket.ticket_number);
        }
    });
}

function createTicketCard(ticket) {
    const isActive = !ticket.is_expired && ticket.booking_status === 'Confirmed';
    const isPast = new Date(ticket.journey_date) < new Date();
    const status = ticket.is_expired ? 'expired' : (isActive ? 'active' : 'cancelled');
    
    // Icon based on ticket type
    const icon = ticket.type === 'KSRTC' ? '🚌' : ticket.type === 'TRAIN' ? '🚂' : '✈️';
    
    return `
        <div class="ticket-card ${status}">
            <div class="ticket-header">
                <div class="ticket-type-badge">${icon} ${ticket.type}</div>
                <div class="ticket-status-badge ${status}">
                    ${status === 'active' ? '✅ Active' : (status === 'expired' ? '⏰ Expired' : '❌ Cancelled')}
                </div>
                <div class="ticket-number">
                    ${ticket.ticket_number || 'N/A'}
                </div>
            </div>
            
            <div class="ticket-body">
                <div class="ticket-route">
                    <div class="route-point">
                        <div class="point-label">From</div>
                        <div class="point-name">${ticket.from}</div>
                    </div>
                    <div class="route-arrow">→</div>
                    <div class="route-point">
                        <div class="point-label">To</div>
                        <div class="point-name">${ticket.to}</div>
                    </div>
                </div>
                
                <div class="ticket-details-grid">
                    <div class="ticket-detail">
                        <strong>Date:</strong>
                        <span>${formatDate(ticket.journey_date)}</span>
                    </div>
                    ${ticket.type === 'KSRTC' ? `
                        <div class="ticket-detail">
                            <strong>Time:</strong>
                            <span>${ticket.departure_time || 'N/A'}</span>
                        </div>
                        <div class="ticket-detail">
                            <strong>Bus:</strong>
                            <span>${ticket.bus_number || 'N/A'}</span>
                        </div>
                        <div class="ticket-detail">
                            <strong>Type:</strong>
                            <span>${ticket.bus_type || 'N/A'}</span>
                        </div>
                        <div class="ticket-detail">
                            <strong>Seat(s):</strong>
                            <span>${ticket.seat_numbers}</span>
                        </div>
                    ` : ticket.type === 'TRAIN' ? `
                        <div class="ticket-detail">
                            <strong>Train:</strong>
                            <span>${ticket.train_number} - ${ticket.train_name}</span>
                        </div>
                        <div class="ticket-detail">
                            <strong>PNR:</strong>
                            <span>${ticket.pnr}</span>
                        </div>
                        <div class="ticket-detail">
                            <strong>Class:</strong>
                            <span>${ticket.coach_type}</span>
                        </div>
                        <div class="ticket-detail">
                            <strong>Berth(s):</strong>
                            <span>${ticket.berth_numbers}</span>
                        </div>
                    ` : `
                        <div class="ticket-detail">
                            <strong>Flight:</strong>
                            <span>${ticket.flight_number} - ${ticket.airline_name}</span>
                        </div>
                        <div class="ticket-detail">
                            <strong>PNR:</strong>
                            <span>${ticket.pnr}</span>
                        </div>
                        <div class="ticket-detail">
                            <strong>Class:</strong>
                            <span>${ticket.travel_class}</span>
                        </div>
                        <div class="ticket-detail">
                            <strong>Seat(s):</strong>
                            <span>${ticket.seat_numbers}</span>
                        </div>
                    `}
                    <div class="ticket-detail">
                        <strong>Fare:</strong>
                        <span>₹${ticket.total_fare.toFixed(2)}</span>
                    </div>
                </div>
                
                <div class="ticket-passenger">
                    <strong>Passenger:</strong> ${ticket.passenger_name}
                </div>
                
                ${isActive ? `
                    <div class="ticket-qr">
                        <div id="qr-${ticket.ticket_number}"></div>
                        <p>Show this QR code for verification</p>
                    </div>
                    <div class="ticket-actions">
                        <button class="btn-cancel" onclick="cancelTicket(${ticket.booking_id}, '${ticket.type}')">❌ Cancel Ticket</button>
                    </div>
                ` : ''}
                
                <div class="ticket-footer">
                    <div class="booking-ref">Booking ID: ${ticket.booking_id} | Booked: ${formatDate(ticket.booked_at)}</div>
                    ${ticket.is_expired ? `<div class="expiry-notice">Expired${ticket.expiry_datetime ? ' on ' + formatDateTime(ticket.expiry_datetime) : ''}</div>` : ''}
                </div>
            </div>
        </div>
    `;
}

function generateQRCode(ticketNumber, bookingRef) {
    const qrElement = document.getElementById(`qr-${ticketNumber}`);
    if (!qrElement) return;
    
    // Clear existing QR
    qrElement.innerHTML = '';
    
    // Generate new QR code
    new QRCode(qrElement, {
        text: bookingRef,
        width: 150,
        height: 150,
        colorDark: "#000000",
        colorLight: "#ffffff",
        correctLevel: QRCode.CorrectLevel.H
    });
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-IN', options);
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return date.toLocaleString('en-IN', options);
}

// Filter tickets
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        
        const filter = e.target.dataset.filter;
        let filtered = allTickets;
        
        if (filter === 'active') {
            filtered = allTickets.filter(t => !t.is_expired && t.booking_status === 'Confirmed');
        } else if (filter === 'expired') {
            filtered = allTickets.filter(t => t.is_expired);
        } else if (filter === 'cancelled') {
            filtered = allTickets.filter(t => t.booking_status === 'Cancelled');
        }
        
        displayTickets(filtered);
    });
});

// Cancel ticket function
async function cancelTicket(bookingId, ticketType) {
    if (!confirm('Are you sure you want to cancel this ticket? This action cannot be undone.')) {
        return;
    }
    
    try {
        const endpoint = ticketType === 'KSRTC' 
            ? `/api/ksrtc/cancel/${bookingId}` 
            : ticketType === 'TRAIN'
            ? `/api/train/cancel/${bookingId}`
            : `/api/flight/cancel/${bookingId}`;
        
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${auth.token}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ Ticket cancelled successfully!');
            // Reload tickets to reflect changes
            await loadTickets();
        } else {
            alert('❌ ' + data.message);
        }
    } catch (error) {
        console.error('Error cancelling ticket:', error);
        alert('❌ Failed to cancel ticket. Please try again.');
    }
}

// Make cancelTicket globally accessible
window.cancelTicket = cancelTicket;
