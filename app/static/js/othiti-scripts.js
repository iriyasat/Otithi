/*
Othiti - Home Sharing Platform
Custom JavaScript Functions
*/

(function ($) {
    "use strict";

    // Preloader
    $(window).on('load', function () {
        if ($('#js-preloader').length) {
            $('#js-preloader').delay(100).fadeOut(500);
        }
    });

    // Mobile Menu
    $('.menu-trigger').on('click', function () {
        $(this).toggleClass('active');
        $('.header-area .nav').slideToggle(200);
    });

    // Menu Trigger
    $('.menu-trigger').on('click', function () {
        $(this).toggleClass('active');
        $('.header-area .nav').slideToggle(200);
    });

    // Menu Hover
    $('.header-area .nav li a').on('mouseenter', function () {
        $(this).parent().siblings().find('a').addClass('fade-out');
    });

    $('.header-area .nav li a').on('mouseleave', function () {
        $(this).parent().siblings().find('a').removeClass('fade-out');
    });

    // Sticky Header
    $(window).on('scroll', function () {
        if ($(this).scrollTop() > 0) {
            $('.header-area').addClass('background-header');
        } else {
            $('.header-area').removeClass('background-header');
        }
    });

    // Banner Slider Auto-Play
    function bannerSwitcher() {
        var next = $('.sec-1-input').filter(':checked').next('.sec-1-input');
        if (next.length) {
            next.prop('checked', true);
        } else {
            $('.sec-1-input').first().prop('checked', true);
        }
    }

    var bannerTimer = setInterval(bannerSwitcher, 5000);

    // Banner Controls
    $('.controls label').on('click', function () {
        clearInterval(bannerTimer);
        bannerTimer = setInterval(bannerSwitcher, 5000);
    });

    // Smooth Scrolling for Anchor Links
    $('a[href*="#"]').on('click', function (e) {
        if (this.hash !== '') {
            e.preventDefault();
            var hash = this.hash;
            $('html, body').animate({
                scrollTop: $(hash).offset().top - 70
            }, 800);
        }
    });

    // Form Validation for Search Form
    $('#search-form').on('submit', function (e) {
        e.preventDefault();
        
        var location = $('#chooseLocation').val();
        var price = $('#choosePrice').val();
        
        if (location === 'Select Location' || price === 'Price Range') {
            alert('Please select both location and price range to search.');
            return false;
        }
        
        // Here you would normally send the data to your backend
        console.log('Search criteria:', {
            location: location,
            price: price
        });
        
        // For demo purposes, show an alert
        alert('Searching for properties in ' + location + ' with price range ' + price);
    });

    // Image Lazy Loading
    $("img").attr("loading", "lazy");

    // Animation on Scroll
    function animateOnScroll() {
        $('.section-heading, .item, .info-item').each(function () {
            var elementTop = $(this).offset().top;
            var elementBottom = elementTop + $(this).outerHeight();
            var viewportTop = $(window).scrollTop();
            var viewportBottom = viewportTop + $(window).height();

            if (elementBottom > viewportTop && elementTop < viewportBottom) {
                $(this).addClass('animate-in');
            }
        });
    }

    $(window).on('scroll', animateOnScroll);
    $(document).ready(animateOnScroll);

    // Owl Carousel Initialization
    if ($('.owl-carousel').length) {
        $('.owl-cites-town').owlCarousel({
            items: 4,
            loop: true,
            dots: false,
            nav: true,
            autoplay: true,
            margin: 30,
            responsive: {
                992: {
                    items: 4
                },
                768: {
                    items: 2
                },
                480: {
                    items: 1
                }
            }
        });

        $('.owl-weekly-offers').owlCarousel({
            items: 3,
            loop: true,
            dots: false,
            nav: true,
            autoplay: true,
            margin: 30,
            responsive: {
                992: {
                    items: 3
                },
                768: {
                    items: 2
                },
                480: {
                    items: 1
                }
            }
        });
    }

    // Best Locations Interactive Options
    $(".option").on('click', function () {
        $(".option").removeClass("active");
        $(this).addClass("active");
    });

    // Back to Top Button
    var backToTopButton = $('<div class="back-to-top"><i class="fa fa-arrow-up"></i></div>');
    $('body').append(backToTopButton);

    $(window).on('scroll', function () {
        if ($(this).scrollTop() > 300) {
            $('.back-to-top').fadeIn();
        } else {
            $('.back-to-top').fadeOut();
        }
    });

    $('.back-to-top').on('click', function () {
        $('html, body').animate({
            scrollTop: 0
        }, 800);
    });

    // Tab Functionality
    $('.tab-links a').on('click', function (e) {
        e.preventDefault();
        var currentAttrValue = $(this).attr('href');

        // Show/Hide Tabs
        $('.tabs ' + currentAttrValue).show().siblings().hide();

        // Change/remove current tab to active
        $(this).parent('li').addClass('active').siblings().removeClass('active');
    });

    // Input Focus Effects
    $('input, textarea, select').on('focus', function () {
        $(this).parent().addClass('focused');
    });

    $('input, textarea, select').on('blur', function () {
        if ($(this).val() === '') {
            $(this).parent().removeClass('focused');
        }
    });

    // Property Cards Hover Effect
    $('.item').on('mouseenter', function () {
        $(this).addClass('hovered');
    });

    $('.item').on('mouseleave', function () {
        $(this).removeClass('hovered');
    });

    // Search Results Counter
    function updateResultsCounter() {
        var visibleItems = $('.amazing-deals .item:visible').length;
        if ($('.results-counter').length === 0) {
            $('.amazing-deals .section-heading').append('<p class="results-counter">Showing ' + visibleItems + ' properties</p>');
        } else {
            $('.results-counter').text('Showing ' + visibleItems + ' properties');
        }
    }

    // Call counter on page load
    if ($('.amazing-deals').length) {
        updateResultsCounter();
    }

    // Price Formatter
    function formatPrice(price) {
        return '৳' + price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    // Load More Functionality
    $('.load-more-btn').on('click', function () {
        var button = $(this);
        button.text('Loading...');
        
        setTimeout(function () {
            // Simulate loading more content
            button.text('Load More Properties');
            updateResultsCounter();
        }, 1000);
    });

    // Toast Notification System
    function showToast(message, type = 'info') {
        var toastClass = 'toast-' + type;
        var toast = $('<div class="toast ' + toastClass + '">' + message + '</div>');
        
        $('body').append(toast);
        
        setTimeout(function () {
            toast.addClass('show');
        }, 100);
        
        setTimeout(function () {
            toast.removeClass('show');
            setTimeout(function () {
                toast.remove();
            }, 300);
        }, 3000);
    }

    // Booking Button Click Handler
    $('.main-button a[href="#"]').on('click', function (e) {
        e.preventDefault();
        showToast('Booking functionality will be available soon!', 'info');
    });

    // Property Wishlist Toggle
    $('.wishlist-btn').on('click', function (e) {
        e.preventDefault();
        $(this).toggleClass('active');
        
        if ($(this).hasClass('active')) {
            showToast('Added to wishlist!', 'success');
        } else {
            showToast('Removed from wishlist!', 'info');
        }
    });

    // Real-time Search
    $('#live-search').on('keyup', function () {
        var value = $(this).val().toLowerCase();
        $('.property-item').filter(function () {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
        });
        updateResultsCounter();
    });

    // Progress Bar Animation
    function animateProgressBars() {
        $('.progress-bar').each(function () {
            var progressWidth = $(this).data('width');
            $(this).css('width', progressWidth + '%');
        });
    }

    $(window).on('scroll', function () {
        if ($('.progress-bar').length && !$('.progress-bar').hasClass('animated')) {
            var progressTop = $('.progress-bar').offset().top;
            var windowBottom = $(window).scrollTop() + $(window).height();
            
            if (progressTop < windowBottom) {
                $('.progress-bar').addClass('animated');
                animateProgressBars();
            }
        }
    });

    // Cookie Consent
    if (!localStorage.getItem('cookieConsent')) {
        var cookieBanner = $('<div class="cookie-banner">This website uses cookies to improve your experience. <button class="accept-cookies">Accept</button></div>');
        $('body').append(cookieBanner);
        
        $('.accept-cookies').on('click', function () {
            localStorage.setItem('cookieConsent', 'true');
            $('.cookie-banner').fadeOut();
        });
    }

    // Window Resize Handler
    $(window).on('resize', function () {
        if ($(window).width() > 992) {
            $('.header-area .nav').show();
        } else {
            $('.header-area .nav').hide();
        }
    });

    // Initialize tooltips if Bootstrap is available
    if (typeof $().tooltip === 'function') {
        $('[data-toggle="tooltip"]').tooltip();
    }

    // Initialize popovers if Bootstrap is available
    if (typeof $().popover === 'function') {
        $('[data-toggle="popover"]').popover();
    }

    // Page Load Analytics (placeholder)
    function trackPageView() {
        // This would integrate with your analytics service
        console.log('Page view tracked:', window.location.pathname);
    }

    // Track page view on load
    $(document).ready(function () {
        trackPageView();
    });

    // Error Handling for Images
    $('img').on('error', function () {
        $(this).attr('src', '/static/images/placeholder.jpg');
    });

    // Auto-hide flash messages
    $('.flash-message').delay(5000).fadeOut(500);

})(jQuery);

// Additional utility functions
window.OthitiUtils = {
    // Format currency
    formatCurrency: function (amount) {
        return '৳' + amount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    },
    
    // Validate email
    validateEmail: function (email) {
        var re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    // Validate phone number (Bangladesh format)
    validatePhone: function (phone) {
        var re = /^(\+88)?01[3-9]\d{8}$/;
        return re.test(phone);
    },
    
    // Get current location
    getCurrentLocation: function (callback) {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(callback);
        } else {
            console.log("Geolocation is not supported by this browser.");
        }
    },
    
    // Debounce function
    debounce: function (func, wait, immediate) {
        var timeout;
        return function () {
            var context = this, args = arguments;
            var later = function () {
                timeout = null;
                if (!immediate) func.apply(context, args);
            };
            var callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(context, args);
        };
    }
}; 