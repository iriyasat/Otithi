// Navbar toggle for mobile (Bootstrap handles this, but for custom toggles you can use this)
document.addEventListener('DOMContentLoaded', function () {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Listing form validation
    const listingForms = document.querySelectorAll('form[action*="listing"]');
    listingForms.forEach(form => {
        form.addEventListener('submit', function (e) {
            let valid = true;
            const requiredFields = ['name', 'location', 'description', 'price_per_night', 'host_name'];
            requiredFields.forEach(field => {
                const input = form.querySelector(`[name="${field}"]`);
                if (input && !input.value.trim()) {
                    valid = false;
                    input.classList.add('is-invalid');
                } else if (input) {
                    input.classList.remove('is-invalid');
                }
            });
            if (!valid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });
}); 