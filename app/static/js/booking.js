/**
 * Otithi Booking JavaScript
 * Booking management and interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeBooking();
});

function initializeBooking() {
    // Initialize booking form validations
    initializeBookingForm();
    
    // Initialize booking actions
    initializeBookingActions();
    
    // Initialize booking calendar
    initializeBookingCalendar();
}

/**
 * Initialize booking form functionality
 */
function initializeBookingForm() {
    const bookingForm = document.querySelector('.booking-form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const checkin = this.querySelector('input[name="checkin"]').value;
            const checkout = this.querySelector('input[name="checkout"]').value;
            const guests = this.querySelector('input[name="guests"]').value;
            
            if (!checkin || !checkout) {
                showNotification('Please select check-in and check-out dates.', 'error');
                return;
            }
            
            if (new Date(checkin) >= new Date(checkout)) {
                showNotification('Check-out date must be after check-in date.', 'error');
                return;
            }
            
            if (!guests || guests < 1) {
                showNotification('Please select number of guests.', 'error');
                return;
            }
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            submitBtn.disabled = true;
            
            // Simulate booking submission
            setTimeout(() => {
                showNotification('Booking request submitted successfully!', 'success');
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
                
                // Redirect to booking confirmation
                window.location.href = '/booking/confirmation';
            }, 2000);
        });
    }
}

/**
 * Initialize booking actions (cancel, modify, etc.)
 */
function initializeBookingActions() {
    // Cancel booking functionality
    const cancelButtons = document.querySelectorAll('[onclick*="cancelBooking"]');
    cancelButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const bookingId = this.dataset.bookingId || 
                             this.getAttribute('onclick').match(/\d+/)[0];
            cancelBooking(bookingId);
        });
    });
    
    // Show booking details functionality
    const detailButtons = document.querySelectorAll('[onclick*="showBookingDetails"]');
    detailButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const bookingId = this.dataset.bookingId || 
                             this.getAttribute('onclick').match(/\d+/)[0];
            showBookingDetails(bookingId);
        });
    });
}

/**
 * Initialize booking calendar functionality
 */
function initializeBookingCalendar() {
    const checkinInput = document.querySelector('input[name="checkin"]');
    const checkoutInput = document.querySelector('input[name="checkout"]');
    
    if (checkinInput && checkoutInput) {
        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];
        checkinInput.min = today;
        checkoutInput.min = today;
        
        // Update checkout min date when checkin changes
        checkinInput.addEventListener('change', function() {
            checkoutInput.min = this.value;
            if (checkoutInput.value && checkoutInput.value <= this.value) {
                checkoutInput.value = '';
            }
        });
        
        // Update total price when dates change
        const updateTotal = () => {
            const checkin = new Date(checkinInput.value);
            const checkout = new Date(checkoutInput.value);
            const pricePerNight = parseFloat(document.querySelector('[data-price-per-night]')?.dataset.pricePerNight || 0);
            
            if (checkin && checkout && checkout > checkin) {
                const nights = Math.ceil((checkout - checkin) / (1000 * 60 * 60 * 24));
                const total = nights * pricePerNight;
                
                const totalElement = document.querySelector('.booking-total');
                if (totalElement) {
                    totalElement.textContent = formatCurrency(total);
                }
            }
        };
        
        checkinInput.addEventListener('change', updateTotal);
        checkoutInput.addEventListener('change', updateTotal);
    }
}

/**
 * Cancel a booking
 * @param {number} bookingId - The booking ID to cancel
 */
async function cancelBooking(bookingId) {
    if (confirm('Are you sure you want to cancel this booking?')) {
        try {
            const config = window.OtithiConfig?.API || {};
            const endpoint = config.BOOKINGS || '/api/bookings';
            const response = await fetch(`${endpoint}/${bookingId}/cancel`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                showNotification('Booking cancelled successfully.', 'success');
                setTimeout(() => {
                    location.reload();
                }, 1500);
            } else {
                const data = await response.json();
                showNotification(data.message || 'Failed to cancel booking.', 'error');
            }
        } catch (error) {
            console.error('Error cancelling booking:', error);
            showNotification('Failed to cancel booking. Please try again.', 'error');
        }
    }
}

/**
 * Show booking details
 * @param {number} bookingId - The booking ID to show details for
 */
function showBookingDetails(bookingId) {
    // Fetch booking details
    const config = window.OtithiConfig?.API || {};
    const endpoint = config.BOOKINGS || '/api/bookings';
    fetch(`${endpoint}/${bookingId}/details`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showBookingDetailsModal(data.booking);
            } else {
                showNotification('Failed to load booking details.', 'error');
            }
        })
        .catch(error => {
            console.error('Error loading booking details:', error);
            showNotification('Failed to load booking details.', 'error');
        });
}

/**
 * Show booking details modal
 * @param {Object} booking - The booking data
 */
function showBookingDetailsModal(booking) {
    const modalContent = `
        <div class="booking-details">
            <div class="row">
                <div class="col-md-6">
                    <h6>Booking Information</h6>
                    <p><strong>Booking ID:</strong> #${booking.booking_id}</p>
                    <p><strong>Check-in:</strong> ${new Date(booking.checkin_date).toLocaleDateString()}</p>
                    <p><strong>Check-out:</strong> ${new Date(booking.checkout_date).toLocaleDateString()}</p>
                    <p><strong>Guests:</strong> ${booking.guests}</p>
                    <p><strong>Total:</strong> ${formatCurrency(booking.total_price)}</p>
                </div>
                <div class="col-md-6">
                    <h6>Property Information</h6>
                    <p><strong>Property:</strong> ${booking.property_title}</p>
                    <p><strong>Location:</strong> ${booking.property_location}</p>
                    <p><strong>Host:</strong> ${booking.host_name}</p>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-12">
                    <h6>Status</h6>
                    <span class="badge bg-${getStatusBadgeClass(booking.status)}">${booking.status}</span>
                </div>
            </div>
        </div>
    `;
    
    showModal('Booking Details', modalContent);
}

/**
 * Get badge class for booking status
 * @param {string} status - The booking status
 * @returns {string} The badge class
 */
function getStatusBadgeClass(status) {
    switch (status.toLowerCase()) {
        case 'confirmed':
            return 'success';
        case 'pending':
            return 'warning';
        case 'cancelled':
            return 'danger';
        case 'completed':
            return 'info';
        default:
            return 'secondary';
    }
}

/**
 * Modify booking dates
 * @param {number} bookingId - The booking ID to modify
 */
async function modifyBooking(bookingId) {
    const newCheckin = prompt('Enter new check-in date (YYYY-MM-DD):');
    const newCheckout = prompt('Enter new check-out date (YYYY-MM-DD):');
    
    if (!newCheckin || !newCheckout) {
        showNotification('Please provide both check-in and check-out dates.', 'error');
        return;
    }
    
    if (new Date(newCheckin) >= new Date(newCheckout)) {
        showNotification('Check-out date must be after check-in date.', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/bookings/${bookingId}/modify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                checkin_date: newCheckin,
                checkout_date: newCheckout
            })
        });
        
        if (response.ok) {
            showNotification('Booking modified successfully.', 'success');
            setTimeout(() => {
                location.reload();
            }, 1500);
        } else {
            const data = await response.json();
            showNotification(data.message || 'Failed to modify booking.', 'error');
        }
    } catch (error) {
        console.error('Error modifying booking:', error);
        showNotification('Failed to modify booking. Please try again.', 'error');
    }
}

/**
 * Request booking refund
 * @param {number} bookingId - The booking ID to request refund for
 */
async function requestRefund(bookingId) {
    const reason = prompt('Please provide a reason for the refund request:');
    
    if (!reason) {
        showNotification('Please provide a reason for the refund request.', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/bookings/${bookingId}/refund`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                reason: reason
            })
        });
        
        if (response.ok) {
            showNotification('Refund request submitted successfully.', 'success');
        } else {
            const data = await response.json();
            showNotification(data.message || 'Failed to submit refund request.', 'error');
        }
    } catch (error) {
        console.error('Error requesting refund:', error);
        showNotification('Failed to submit refund request. Please try again.', 'error');
    }
}

/**
 * Calculate booking total
 * @param {number} pricePerNight - Price per night
 * @param {string} checkin - Check-in date
 * @param {string} checkout - Check-out date
 * @param {number} guests - Number of guests
 * @returns {Object} Object containing nights and total
 */
function calculateBookingTotal(pricePerNight, checkin, checkout, guests = 1) {
    if (!checkin || !checkout) {
        return { nights: 0, total: 0 };
    }
    
    const config = window.OtithiConfig?.APP || {};
    const serviceFeePercentage = config.SERVICE_FEE_PERCENTAGE || 0.15;
    
    const checkinDate = new Date(checkin);
    const checkoutDate = new Date(checkout);
    const nights = Math.ceil((checkoutDate - checkinDate) / (1000 * 60 * 60 * 24));
    const basePrice = nights * pricePerNight * guests;
    const serviceFee = basePrice * serviceFeePercentage;
    const total = basePrice + serviceFee;
    
    return { nights, basePrice, serviceFee, total };
}

/**
 * Update booking summary
 */
function updateBookingSummary() {
    const checkin = document.querySelector('input[name="checkin"]')?.value;
    const checkout = document.querySelector('input[name="checkout"]')?.value;
    const guests = parseInt(document.querySelector('input[name="guests"]')?.value || 1);
    const pricePerNight = parseFloat(document.querySelector('[data-price-per-night]')?.dataset.pricePerNight || 0);
    
    const { nights, total } = calculateBookingTotal(pricePerNight, checkin, checkout, guests);
    
    const nightsElement = document.querySelector('.booking-nights');
    const totalElement = document.querySelector('.booking-total');
    
    if (nightsElement) {
        nightsElement.textContent = nights;
    }
    
    if (totalElement) {
        totalElement.textContent = formatCurrency(total);
    }
} 