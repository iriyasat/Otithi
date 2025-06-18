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

    // Navbar shadow/color on scroll
    const navbar = document.querySelector('.navbar-bd');
    window.addEventListener('scroll', function () {
        if (window.scrollY > 10) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // --- Airbnb-style Mobile Menu Toggle ---
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('.navbar-nav');
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', function () {
            navMenu.classList.toggle('open');
            menuToggle.classList.toggle('open');
        });
    }

    // --- Airbnb-style Section Fade-in with Intersection Observer ---
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    obs.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15 });
        document.querySelectorAll('.section-fade').forEach(section => {
            observer.observe(section);
        });
    } else {
        // fallback to scroll event
        function revealSections() {
            const sections = document.querySelectorAll('.section-fade');
            const trigger = window.innerHeight * 0.92;
            sections.forEach(section => {
                const rect = section.getBoundingClientRect();
                if (rect.top < trigger) {
                    section.classList.add('visible');
                }
            });
        }
        window.addEventListener('scroll', revealSections);
        revealSections();
    }

    // --- Airbnb-style Search Bar Animation ---
    const searchBar = document.querySelector('.search-bar-animated');
    if (searchBar) {
        searchBar.addEventListener('focus', function () {
            searchBar.classList.add('active');
        });
        searchBar.addEventListener('blur', function () {
            searchBar.classList.remove('active');
        });
    }

    // Button ripple/hover effect
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('mouseenter', function () {
            btn.classList.add('fade-in');
        });
        btn.addEventListener('mouseleave', function () {
            btn.classList.remove('fade-in');
        });
    });
}); 