// Initialize the map
 // Handle form submission
document.getElementById('locationForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const location = document.getElementById('location').value;
    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${location}`)
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) {
                const lat = data[0].lat;
                const lon = data[0].lon;
                map.setView([lat, lon], 13);
                L.marker([lat, lon]).addTo(map)
                    .bindPopup(`<b>${location}</b>`)
                    .openPopup();
            } else {
                alert('Location not found');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while searching for the location');
        });
});
