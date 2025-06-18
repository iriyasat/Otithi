/*
Bangladesh-Inspired Interactive JS
Author: Your Name
Description: Clean, robust JavaScript for Flask app with Bangladesh color theme.
*/

/* =========================
   Airbnb-Style UI Interactions
   ========================= */
document.addEventListener('DOMContentLoaded', function () {
    // --- Mobile Nav Toggle ---
    const menuToggle = document.querySelector('.menu-toggle');
    const mobileNav = document.querySelector('.mobile-nav');
    if (menuToggle && mobileNav) {
        menuToggle.addEventListener('click', function () {
            const isOpen = mobileNav.classList.toggle('open');
            menuToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        });
        mobileNav.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                mobileNav.classList.remove('open');
                menuToggle.setAttribute('aria-expanded', 'false');
            });
        });
    }

    // --- Profile Dropdown (Bootstrap handles dropdowns) ---
    // No custom JS needed for dropdown-menu if using Bootstrap

    // --- Search Bar Focus Animation ---
    document.querySelectorAll('.search-bar-airbnb input').forEach(input => {
        input.addEventListener('focus', function () {
            this.closest('.search-bar-airbnb').classList.add('active');
        });
        input.addEventListener('blur', function () {
            this.closest('.search-bar-airbnb').classList.remove('active');
        });
    });

    // --- Section Fade-In on Scroll ---
    const fadeSections = document.querySelectorAll('.section-fade');
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    obs.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15 });
        fadeSections.forEach(section => observer.observe(section));
    } else {
        function revealSections() {
            const trigger = window.innerHeight * 0.92;
            fadeSections.forEach(section => {
                const rect = section.getBoundingClientRect();
                if (rect.top < trigger) {
                    section.classList.add('visible');
                }
            });
        }
        window.addEventListener('scroll', revealSections);
        revealSections();
    }

    // Smooth Scroll for Anchor Links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            // Only handle valid, non-empty hash links
            if (targetId && targetId.length > 1 && document.querySelector(targetId)) {
                e.preventDefault();
                document.querySelector(targetId).scrollIntoView({
                    behavior: 'smooth'
                });
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