/**
 * Admin verification toggle functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Find all verification toggle buttons
    const toggleButtons = document.querySelectorAll('.verification-toggle');
    
    toggleButtons.forEach((btn) => {        
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const userId = this.dataset.userId;
            const originalHtml = this.innerHTML;
            
            if (!userId) {
                console.error('No user ID found on button');
                return;
            }
            
            // Show loading state
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            this.disabled = true;
            
            fetch(`/admin/users/${userId}/toggle-verification`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Update the verification badge in the same row
                    const row = this.closest('tr');
                    const verificationBadge = row.querySelector('td:nth-child(3) .badge');
                    
                    if (verificationBadge) {
                        verificationBadge.textContent = data.status_text;
                        verificationBadge.className = `badge bg-${data.badge_class}`;
                    }
                    
                    // Update the toggle button
                    this.className = `btn btn-outline-${data.btn_class} btn-sm verification-toggle`;
                    this.innerHTML = `<i class="fas fa-${data.btn_icon}"></i>`;
                    this.title = data.btn_title;
                    
                    // Show success feedback briefly
                    const originalTitle = this.title;
                    this.title = '✓ Updated!';
                    setTimeout(() => {
                        this.title = originalTitle;
                    }, 2000);
                } else {
                    alert('Error: ' + data.message);
                    this.innerHTML = originalHtml;
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
                alert('An error occurred while updating verification status: ' + error.message);
                this.innerHTML = originalHtml;
            })
            .finally(() => {
                this.disabled = false;
            });
        });
    });
});
