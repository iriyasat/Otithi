/**
 * Otithi Maps JavaScript
 * Google Maps integration and location functionality
 */

// Global variables for map functionality (only declare if not already declared)
if (typeof map === 'undefined') { var map; }
if (typeof marker === 'undefined') { var marker; }
if (typeof autocomplete === 'undefined') { var autocomplete; }
if (typeof geocoder === 'undefined') { var geocoder; }
if (typeof currentInfoWindow === 'undefined') { var currentInfoWindow; }

document.addEventListener('DOMContentLoaded', function() {
    initializeMaps();
});

function initializeMaps() {
    // Check if Google Maps API is loaded
    if (typeof google !== 'undefined' && google.maps) {
        initializeMapComponents();
    } else {
        // Wait for Google Maps API to load
        window.initMap = initializeMapComponents;
    }
}

/**
 * Initialize map components
 */
function initializeMapComponents() {
    // Initialize map if map container exists
    const mapContainer = document.getElementById('map');
    if (mapContainer) {
        initMap();
    }
    
    // Initialize location search
    initializeLocationSearch();
    
    // Initialize property map
    initializePropertyMap();
}

/**
 * Initialize Google Maps
 */
function initMap() {
    console.log('initMap function called');
    
    // Check if Google Maps API is available
    if (typeof google === 'undefined' || !google.maps) {
        console.error('Google Maps API not loaded');
        return;
    }
    
    // Get configuration
    const config = window.OtithiConfig?.GOOGLE_MAPS || {
        DEFAULT_LOCATION: { lat: 23.8103, lng: 90.4125 }
    };
    
    console.log('Maps config:', config);
    
    // Default location (Dhaka, Bangladesh)
    const defaultLocation = config.DEFAULT_LOCATION;
    
    // Initialize map
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 13,
        center: defaultLocation,
        mapTypeControl: true,
        mapTypeControlOptions: {
            style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
            position: google.maps.ControlPosition.TOP_CENTER,
        },
        zoomControl: true,
        zoomControlOptions: {
            position: google.maps.ControlPosition.RIGHT_CENTER,
        },
        scaleControl: true,
        streetViewControl: true,
        streetViewControlOptions: {
            position: google.maps.ControlPosition.RIGHT_TOP,
        },
        fullscreenControl: false,
        styles: getMapStyles()
    });

    // Initialize geocoder
    geocoder = new google.maps.Geocoder();

    // Initialize autocomplete
    const addressInput = document.getElementById("address");
    if (addressInput) {
        autocomplete = new google.maps.places.Autocomplete(addressInput, {
            componentRestrictions: { country: "bd" }, // Restrict to Bangladesh
            fields: ["address_components", "geometry", "name", "formatted_address"],
            types: ["address"]
        });

        // Autocomplete place changed event
        autocomplete.addListener("place_changed", function() {
            const place = autocomplete.getPlace();
            
            if (!place.geometry) {
                showNotification("No details available for input: '" + place.name + "'", "error");
                return;
            }

            // Update map and marker
            updateMapLocation(place.geometry.location, place.formatted_address);
            
            // Parse address components
            parseAddressComponents(place.address_components);
        });
    }

    // Map click event to allow manual location selection
    map.addListener("click", function(event) {
        updateMapLocation(event.latLng);
        
        // Reverse geocode to get address
        geocoder.geocode(
            { location: event.latLng },
            function(results, status) {
                if (status === "OK" && results[0]) {
                    const addressInput = document.getElementById("address");
                    if (addressInput) {
                        addressInput.value = results[0].formatted_address;
                        parseAddressComponents(results[0].address_components);
                    }
                }
            }
        );
    });

    // Try to get user's current location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                
                // Center map on user's location if it's in Bangladesh
                if (userLocation.lat >= 20.5 && userLocation.lat <= 26.5 && 
                    userLocation.lng >= 88.0 && userLocation.lng <= 93.0) {
                    map.setCenter(userLocation);
                    map.setZoom(15);
                }
            },
            function() {
                console.log("Unable to get user's location");
            }
        );
    }
}

/**
 * Initialize location search functionality
 */
function initializeLocationSearch() {
    const locationInput = document.querySelector('input[name="location"]');
    if (locationInput) {
        const autocomplete = new google.maps.places.Autocomplete(locationInput, {
            componentRestrictions: { country: "bd" },
            types: ["(cities)"]
        });
        
        autocomplete.addListener("place_changed", function() {
            const place = autocomplete.getPlace();
            if (place.geometry) {
                // Update search form with selected location
                locationInput.value = place.formatted_address;
                
                // Trigger search if search form exists
                const searchForm = document.querySelector('.search-form');
                if (searchForm) {
                    searchForm.submit();
                }
            }
        });
    }
}

/**
 * Initialize property map for listing details
 */
function initializePropertyMap() {
    const propertyMap = document.getElementById('property-map');
    if (propertyMap) {
        const lat = parseFloat(propertyMap.dataset.lat);
        const lng = parseFloat(propertyMap.dataset.lng);
        const title = propertyMap.dataset.title;
        
        if (lat && lng) {
            const propertyLocation = { lat, lng };
            
            const propertyMapInstance = new google.maps.Map(propertyMap, {
                zoom: 15,
                center: propertyLocation,
                mapTypeControl: false,
                streetViewControl: false,
                fullscreenControl: false,
                styles: getMapStyles()
            });
            
            // Add marker for property
            const propertyMarker = new google.maps.Marker({
                position: propertyLocation,
                map: propertyMapInstance,
                title: title,
                icon: {
                    url: '/static/img/map-marker.png',
                    scaledSize: new google.maps.Size(32, 32)
                }
            });
            
            // Add info window
            const infoWindow = new google.maps.InfoWindow({
                content: `<div><strong>${title}</strong></div>`
            });
            
            propertyMarker.addListener("click", () => {
                infoWindow.open(propertyMapInstance, propertyMarker);
            });
        }
    }
}

/**
 * Update map location and marker
 * @param {google.maps.LatLng} location - The location to set
 * @param {string} address - The formatted address
 */
function updateMapLocation(location, address = null) {
    // Update map center
    map.setCenter(location);
    map.setZoom(15);
    
    // Remove existing marker
    if (marker) {
        marker.setMap(null);
    }
    
    // Add new marker
    marker = new google.maps.Marker({
        position: location,
        map: map,
        draggable: true,
        title: address || "Selected Location"
    });
    
    // Add drag listener to update address
    marker.addListener("dragend", function() {
        const position = marker.getPosition();
        
        // Update coordinates first
        updateLocationInputs(position);
        
        // Then reverse geocode for address
        geocoder.geocode(
            { location: position },
            function(results, status) {
                if (status === "OK" && results[0]) {
                    const addressInput = document.getElementById("address");
                    if (addressInput) {
                        addressInput.value = results[0].formatted_address;
                        parseAddressComponents(results[0].address_components);
                    }
                }
            }
        );
    });
    
    // Update hidden input fields
    updateLocationInputs(location);
}

/**
 * Parse address components and update form fields
 * @param {Array} addressComponents - Address components from Google Places API
 */
function parseAddressComponents(addressComponents) {
    let streetNumber = '';
    let route = '';
    let locality = '';
    let administrativeArea = '';
    let postalCode = '';
    let country = '';
    
    for (const component of addressComponents) {
        const type = component.types[0];
        
        switch (type) {
            case 'street_number':
                streetNumber = component.long_name;
                break;
            case 'route':
                route = component.long_name;
                break;
            case 'locality':
                locality = component.long_name;
                break;
            case 'administrative_area_level_1':
                administrativeArea = component.long_name;
                break;
            case 'postal_code':
                postalCode = component.long_name;
                break;
            case 'country':
                country = component.long_name;
                break;
        }
    }
    
    // Update form fields if they exist
    const streetInput = document.getElementById('street');
    const cityInput = document.getElementById('city');
    const stateInput = document.getElementById('state');
    const zipInput = document.getElementById('zip');
    
    if (streetInput) {
        streetInput.value = `${streetNumber} ${route}`.trim();
    }
    if (cityInput) {
        cityInput.value = locality;
    }
    if (stateInput) {
        stateInput.value = administrativeArea;
    }
    if (zipInput) {
        zipInput.value = postalCode;
    }
}

/**
 * Update hidden location input fields
 * @param {google.maps.LatLng} location - The location coordinates
 */
function updateLocationInputs(location) {
    const latInput = document.getElementById('latitude');
    const lngInput = document.getElementById('longitude');
    
    const lat = location.lat();
    const lng = location.lng();
    
    if (latInput) {
        latInput.value = lat;
    }
    if (lngInput) {
        lngInput.value = lng;
    }
    
    // Update coordinate display elements
    updateCoordinateDisplay(lat, lng);
}

/**
 * Get custom map styles
 * @returns {Array} Array of map style objects
 */
function getMapStyles() {
    return [
        {
            "featureType": "all",
            "elementType": "labels.text.fill",
            "stylers": [
                {
                    "saturation": 36
                },
                {
                    "color": "#333333"
                },
                {
                    "lightness": 40
                }
            ]
        },
        {
            "featureType": "all",
            "elementType": "labels.text.stroke",
            "stylers": [
                {
                    "visibility": "on"
                },
                {
                    "color": "#ffffff"
                },
                {
                    "lightness": 16
                }
            ]
        },
        {
            "featureType": "all",
            "elementType": "labels.icon",
            "stylers": [
                {
                    "visibility": "off"
                }
            ]
        },
        {
            "featureType": "administrative",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "#fefefe"
                },
                {
                    "lightness": 20
                }
            ]
        },
        {
            "featureType": "administrative",
            "elementType": "geometry.stroke",
            "stylers": [
                {
                    "color": "#fefefe"
                },
                {
                    "lightness": 17
                },
                {
                    "weight": 1.2
                }
            ]
        },
        {
            "featureType": "landscape",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#f5f5f5"
                },
                {
                    "lightness": 20
                }
            ]
        },
        {
            "featureType": "poi",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#f5f5f5"
                },
                {
                    "lightness": 21
                }
            ]
        },
        {
            "featureType": "poi.park",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#dedede"
                },
                {
                    "lightness": 21
                }
            ]
        },
        {
            "featureType": "road.highway",
            "elementType": "geometry.fill",
            "stylers": [
                {
                    "color": "#ffffff"
                },
                {
                    "lightness": 17
                }
            ]
        },
        {
            "featureType": "road.highway",
            "elementType": "geometry.stroke",
            "stylers": [
                {
                    "color": "#ffffff"
                },
                {
                    "lightness": 29
                },
                {
                    "weight": 0.2
                }
            ]
        },
        {
            "featureType": "road.arterial",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#ffffff"
                },
                {
                    "lightness": 18
                }
            ]
        },
        {
            "featureType": "road.local",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#ffffff"
                },
                {
                    "lightness": 16
                }
            ]
        },
        {
            "featureType": "transit",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#f2f2f2"
                },
                {
                    "lightness": 19
                }
            ]
        },
        {
            "featureType": "water",
            "elementType": "geometry",
            "stylers": [
                {
                    "color": "#c9c9c9"
                },
                {
                    "lightness": 17
                }
            ]
        }
    ];
}

/**
 * Show nearby properties on map
 * @param {Array} properties - Array of property data
 */
function showNearbyProperties(properties) {
    // Clear existing markers
    if (window.propertyMarkers) {
        window.propertyMarkers.forEach(marker => marker.setMap(null));
    }
    window.propertyMarkers = [];
    
    // Add markers for each property
    properties.forEach(property => {
        const marker = new google.maps.Marker({
            position: { lat: property.lat, lng: property.lng },
            map: map,
            title: property.title,
            icon: {
                url: '/static/img/property-marker.png',
                scaledSize: new google.maps.Size(24, 24)
            }
        });
        
        // Add info window
        const infoWindow = new google.maps.InfoWindow({
            content: `
                <div class="property-info-window">
                    <h6>${property.title}</h6>
                    <p>${property.price}</p>
                    <a href="/listing/${property.id}" class="btn btn-sm btn-primary">View Details</a>
                </div>
            `
        });
        
        marker.addListener("click", () => {
            if (currentInfoWindow) {
                currentInfoWindow.close();
            }
            infoWindow.open(map, marker);
            currentInfoWindow = infoWindow;
        });
        
        window.propertyMarkers.push(marker);
    });
}

/**
 * Get distance between two points
 * @param {google.maps.LatLng} point1 - First point
 * @param {google.maps.LatLng} point2 - Second point
 * @returns {number} Distance in kilometers
 */
function getDistance(point1, point2) {
    return google.maps.geometry.spherical.computeDistanceBetween(point1, point2) / 1000;
}

/**
 * Draw route between two points
 * @param {google.maps.LatLng} origin - Origin point
 * @param {google.maps.LatLng} destination - Destination point
 */
function drawRoute(origin, destination) {
    const directionsService = new google.maps.DirectionsService();
    const directionsRenderer = new google.maps.DirectionsRenderer({
        suppressMarkers: true
    });
    
    directionsRenderer.setMap(map);
    
    directionsService.route({
        origin: origin,
        destination: destination,
        travelMode: google.maps.TravelMode.DRIVING
    }, (response, status) => {
        if (status === 'OK') {
            directionsRenderer.setDirections(response);
        } else {
            showNotification('Unable to calculate route', 'error');
        }
    });
}

/**
 * Get current location using browser geolocation
 */
function getCurrentLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                const currentLocation = { lat: lat, lng: lng };
                
                // Update map center and marker
                if (map) {
                    map.setCenter(currentLocation);
                    map.setZoom(15);
                    
                    // Update or create marker
                    if (marker) {
                        marker.setPosition(currentLocation);
                    } else {
                        marker = new google.maps.Marker({
                            position: currentLocation,
                            map: map,
                            title: 'Current Location'
                        });
                    }
                }
                
                // Reverse geocode to get address
                if (geocoder) {
                    geocoder.geocode({ location: currentLocation }, function(results, status) {
                        if (status === 'OK' && results[0]) {
                            const address = results[0].formatted_address;
                            
                            // Update address field if it exists
                            const addressField = document.getElementById('address');
                            if (addressField) {
                                addressField.value = address;
                            }
                            
                            // Parse address components
                            const components = results[0].address_components;
                            let city = '';
                            let state = '';
                            let country = '';
                            
                            components.forEach(component => {
                                if (component.types.includes('locality')) {
                                    city = component.long_name;
                                } else if (component.types.includes('administrative_area_level_1')) {
                                    state = component.long_name;
                                } else if (component.types.includes('country')) {
                                    country = component.long_name;
                                }
                            });
                            
                            // Update form fields
                            const cityField = document.getElementById('city');
                            const stateField = document.getElementById('state');
                            const countryField = document.getElementById('country');
                            const latField = document.getElementById('latitude');
                            const lngField = document.getElementById('longitude');
                            
                            if (cityField) cityField.value = city;
                            if (stateField) stateField.value = state;
                            if (countryField) countryField.value = country;
                            if (latField) latField.value = lat;
                            if (lngField) lngField.value = lng;
                            
                            // Update coordinate display elements
                            updateCoordinateDisplay(lat, lng);
                            
                            showNotification('Current location detected successfully!', 'success');
                        }
                    });
                }
            },
            function(error) {
                let errorMessage = 'Unable to get your location. ';
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        errorMessage += 'Please allow location access.';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMessage += 'Location information unavailable.';
                        break;
                    case error.TIMEOUT:
                        errorMessage += 'Location request timed out.';
                        break;
                    default:
                        errorMessage += 'An unknown error occurred.';
                        break;
                }
                showNotification(errorMessage, 'error');
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 300000
            }
        );
    } else {
        showNotification('Geolocation is not supported by this browser.', 'error');
    }
}

/**
 * Show notification message
 */
function showNotification(message, type = 'info') {
    // Try to use existing notification system or create a simple alert
    if (typeof showAlert === 'function') {
        showAlert(message, type);
    } else {
        alert(message);
    }
}

/**
 * Update coordinate display elements
 * @param {number} lat - Latitude
 * @param {number} lng - Longitude
 */
function updateCoordinateDisplay(lat, lng) {
    const latDisplay = document.getElementById('latitude-display');
    const lngDisplay = document.getElementById('longitude-display');
    
    if (latDisplay) {
        latDisplay.textContent = lat.toFixed(6);
    }
    if (lngDisplay) {
        lngDisplay.textContent = lng.toFixed(6);
    }
} 