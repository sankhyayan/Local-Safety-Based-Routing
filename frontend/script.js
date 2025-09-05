// Initialize map centered on Chandigarh
const map = L.map('map').setView([30.7333, 76.7794], 13);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// Store current route layer for cleanup
let currentRouteLayer = null;

async function getRoute() {
    const startInput = document.getElementById('start').value.trim();
    const endInput = document.getElementById('end').value.trim();
    
    // Validate inputs
    if (!startInput || !endInput) {
        alert('Please enter both start and end coordinates');
        return;
    }
    
    const start = startInput.split(',');
    const end = endInput.split(',');
    
    // Validate coordinate format
    if (start.length !== 2 || end.length !== 2) {
        alert('Please enter coordinates in format: lat,lon');
        return;
    }
    
    const [startLat, startLon] = start.map(coord => parseFloat(coord.trim()));
    const [endLat, endLon] = end.map(coord => parseFloat(coord.trim()));
    
    // Validate coordinate values
    if (isNaN(startLat) || isNaN(startLon) || isNaN(endLat) || isNaN(endLon)) {
        alert('Please enter valid numeric coordinates');
        return;
    }
    
    console.log(`Route request: ${startLat},${startLon} → ${endLat},${endLon}`);
    
    try {
        const url = `http://localhost:8000/safest-route?start_lat=${startLat}&start_lon=${startLon}&end_lat=${endLat}&end_lon=${endLon}`;
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            alert(`Error: ${data.error}`);
            return;
        }
        
        displayRoute(data);
        
    } catch (error) {
        console.error('Route request failed:', error);
        alert(`Failed to get route: ${error.message}`);
    }
}

function displayRoute(data) {
    // Clear previous route
    if (currentRouteLayer) {
        map.removeLayer(currentRouteLayer);
    }
    
    // Extract and convert coordinates from [lon, lat] to [lat, lon]
    const coordinates = data.safest_route.points.coordinates;
    const route = coordinates.map(point => [point[1], point[0]]);
    
    // Add route to map
    currentRouteLayer = L.polyline(route, {
        color: '#2196F3',
        weight: 5,
        opacity: 0.8
    }).addTo(map);
    
    // Fit map to route
    map.fitBounds(route);
    
    // Show route info
    const distance = (data.safest_route.distance / 1000).toFixed(2);
    const time = Math.round(data.safest_route.time / 60);
    
    alert(`Route found!\nDistance: ${distance} km\nTime: ${time} min\nSafety Score: ${data.score.toFixed(2)}`);
    
    console.log('Route displayed successfully', {
        distance: `${distance} km`,
        time: `${time} min`,
        score: data.score,
        points: route.length
    });
}

// Add markers on map click
map.on('click', function(e) {
    const lat = e.latlng.lat.toFixed(6);
    const lon = e.latlng.lng.toFixed(6);
    
    // Fill start field if empty, otherwise fill end field
    const startField = document.getElementById('start');
    const endField = document.getElementById('end');
    
    if (!startField.value) {
        startField.value = `${lat},${lon}`;
        L.marker([lat, lon]).addTo(map).bindPopup('Start').openPopup();
    } else if (!endField.value) {
        endField.value = `${lat},${lon}`;
        L.marker([lat, lon]).addTo(map).bindPopup('End').openPopup();
    }
});

console.log('Safety Route app initialized');