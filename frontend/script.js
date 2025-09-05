const map = L.map('map').setView([30.7333, 76.7794], 13);  // Chandigarh center
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap'
}).addTo(map);

// Store current route layer to clear it later
let currentRouteLayer = null;

async function getRoute() {
    const start = document.getElementById('start').value.split(',');
    const end = document.getElementById('end').value.split(',');
    
    try {
        const response = await fetch(`http://localhost:8000/safest-route?start_lat=${start[0]}&start_lon=${start[1]}&end_lat=${end[0]}&end_lon=${end[1]}`);
        const data = await response.json();
        
        if (data.error) {
            alert(data.error);
            return;
        }
        
        // Clear previous route
        if (currentRouteLayer) {
            map.removeLayer(currentRouteLayer);
        }
        
        // Extract coordinates and convert to [lat, lon] format
        const coordinates = data.safest_route.points.coordinates;
        const route = coordinates.map(p => [p[1], p[0]]);  // Convert [lon, lat] to [lat, lon]
        
        // Add new route
        currentRouteLayer = L.polyline(route, {
            color: 'blue',
            weight: 5,
            opacity: 0.7
        }).addTo(map);
        
        // Fit map to route bounds
        map.fitBounds(route);
        
        alert(`Safest route score: ${data.score}`);
        
        // Debug: Log coordinates to console
        console.log('Route coordinates:', route);
        console.log('Route bounds:', currentRouteLayer.getBounds());
        
    } catch (error) {
        console.error('Error fetching route:', error);
        alert('Error fetching route. Check console for details.');
    }
}