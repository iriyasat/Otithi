// Common chart options
const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: false
        }
    },
    scales: {
        y: {
            beginAtZero: true
        }
    }
};

// Navigation functionality
document.addEventListener('DOMContentLoaded', function() {
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Active link highlighting
    const currentLocation = location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        }
    });

    // Initialize charts
    initializeCharts();
});

// Logout functionality
function handleLogout(event) {
    event.preventDefault();
    fetch('/api/logout', {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            window.location.href = data.redirect_url;
        } else {
            alert(data.message || 'An error occurred during logout.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred during logout.');
    });
}

// Initialize charts based on user role
function initializeCharts() {
    const userRole = document.body.dataset.userRole;
    
    if (userRole === 'admin') {
        initializeAdminCharts();
    } else if (userRole === 'host') {
        initializeHostCharts();
    } else if (userRole === 'guest') {
        initializeGuestCharts();
    }
}

// Admin charts
function initializeAdminCharts() {
    // User Growth Chart
    const userGrowthCtx = document.getElementById('userGrowthChart')?.getContext('2d');
    if (userGrowthCtx) {
        new Chart(userGrowthCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'New Users',
                    data: [10, 15, 20, 25, 30, 35],
                    borderColor: '#006A4E',
                    backgroundColor: '#006A4E',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: commonOptions
        });
    }

    // Booking Trends Chart
    const bookingTrendsCtx = document.getElementById('bookingTrendsChart')?.getContext('2d');
    if (bookingTrendsCtx) {
        new Chart(bookingTrendsCtx, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Bookings',
                    data: [25, 30, 35, 40, 45, 50],
                    backgroundColor: '#22c55e'
                }]
            },
            options: commonOptions
        });
    }
}

// Host charts
function initializeHostCharts() {
    // Booking Trends Chart
    const bookingTrendsCtx = document.getElementById('bookingTrendsChart')?.getContext('2d');
    if (bookingTrendsCtx) {
        new Chart(bookingTrendsCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Bookings',
                    data: [5, 8, 12, 15, 18, 20],
                    borderColor: '#22c55e',
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: commonOptions
        });
    }

    // Earnings Chart
    const earningsCtx = document.getElementById('earningsChart')?.getContext('2d');
    if (earningsCtx) {
        new Chart(earningsCtx, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Earnings',
                    data: [5000, 8000, 12000, 15000, 18000, 20000],
                    backgroundColor: '#F42A41'
                }]
            },
            options: {
                ...commonOptions,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '৳' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }
}

// Guest charts
function initializeGuestCharts() {
    // Booking History Chart
    const bookingHistoryCtx = document.getElementById('bookingHistoryChart')?.getContext('2d');
    if (bookingHistoryCtx) {
        new Chart(bookingHistoryCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Bookings',
                    data: [2, 3, 4, 5, 6, 7],
                    borderColor: '#006A4E',
                    backgroundColor: '#006A4E',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: commonOptions
        });
    }

    // Spending Chart
    const spendingCtx = document.getElementById('spendingChart')?.getContext('2d');
    if (spendingCtx) {
        new Chart(spendingCtx, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Spending',
                    data: [2000, 3000, 4000, 5000, 6000, 7000],
                    backgroundColor: '#FFD700'
                }]
            },
            options: {
                ...commonOptions,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '৳' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }
} 