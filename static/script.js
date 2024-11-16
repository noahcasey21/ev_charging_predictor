//load data
async function getData(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }
    
        const json = await response.json();
        return json;
    } catch (error) {
        console.error(error.message);
    }
}

function getMapBounds() {
    var bounds = map.getBounds();
    return [bounds.getNorth(), bounds.getSouth(), bounds.getWest(), bounds.getEast()]
}

function displayStations(leftLong, rightLong, bottomLat, topLat, station_data, selectedYear) {
    // Filter station data by map bounds and selected date
    const filtered_station_data = station_data.filter(obj => {
        const openDate = parseDate(obj["Open Date"]);
        return (
            obj.Longitude >= leftLong &&
            obj.Longitude <= rightLong &&
            obj.Latitude >= bottomLat &&
            obj.Latitude <= topLat &&
            obj.Year < selectedYear               
        );
    });

    // Clear existing markers
    map.eachLayer(layer => {
       console.log(layer);
    if (layer instanceof L.CircleMarker) {
        console.log(layer.constructor.name);
            map.removeLayer(layer);
        }
    });

    // Loop through filtered data and add markers
    for (let i = 0; i<filtered_station_data.length; i++) {
        const station = filtered_station_data[i];

        if (station['Algorithm'] === 'Original') {
            L.circleMarker([station['Latitude'], station['Longitude']], { radius: 3, renderer: myRenderer })
                .addTo(map)
                .bindPopup(station['Station Name'] + '<br>' + station['Street Address']
                    + '<br>' + station.City + ', ' + station.State + '<br>Open Date: ' + station['Open Date']);
        }
        else {
            let color;
            switch (station['Algorithm']) {
                case 'Frank':
                    color = 'red';
                    break;
                case 'Noah_C':
                    color = 'green';
                    break;
                case 'Noah_S':
                    color = 'black';
                    break;
                default:
                    color = 'red';
            }

            L.circleMarker([station['Latitude'], station['Longitude']], { radius: 3, renderer: myRenderer })
                .setStyle({ color: color, fillColor: color })
                .addTo(map)
                .bindPopup("Prediction: " + station['Algorithm'] + '<br>' + station.City + ', ' + station.State);
        }
    }
    
}


// Function to get the selected date from the slider
function getYear() {
    return parseInt(dateSlider.value, 10);//Date(minDate.getTime() + dateSlider.value * (1000 * 60 * 60 * 24));
}

// Update the displayed date
function updateDateDisplay() {
    const year = getYear();
    yearSpan.textContent = `Year: ${year}`;// selectedDate.toISOString().split("T")[0];
    
    
}
function loadCities(station_data) {
    // Get unique list of cities
    const selectedYear = getYear();
    const uniqueCities = [...new Set(station_data
        .filter(station => station['Algorithm'] !== 'Original' && station.Year == selectedYear)
        .map(station => `${station.City}, ${station.State}`))];

    // Get the location dropdown element
    const locationDropdown = document.getElementById('locationDropdown');

    // Get the currently selected value
    const selectedValue = locationDropdown.value;

    // Clear existing options
    locationDropdown.innerHTML = '';

    // Add unique cities to the dropdown
    uniqueCities.forEach(city => {
        const option = document.createElement('option');
        option.value = city;
        option.textContent = city;
        locationDropdown.appendChild(option);
    });

    // Restore the previously selected value if it exists
    if (uniqueCities.includes(selectedValue)) {
        locationDropdown.value = selectedValue;
    }
    centerLocation(locationDropdown.value);
}
function centerLocation(location) {
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
}
var maxBounds = [
    [24.396308, -125.000000], // Southwest corner
    [49.384358, -66.934570]   // Northeast corner
]

var map = L.map('map', {
    'center': [33.77, -84.40],
    'zoom': 10,
    'maxBounds': maxBounds,
    'zoomSnap': 0.5,
    'minZoom': 4,
    'maxZoom': 15
});

var myRenderer = L.canvas({ padding: 0.5 });

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

const loaderContainer = document.getElementById('loader-container');
// Helper function to parse the date
const parseDate = (dateString) => new Date(dateString);

// Initialize date slider variables
const minDate = new Date("1990-01-01");
const maxDate = new Date("2024-12-31");
const dayDifference = (maxDate - minDate) / (1000 * 60 * 60 * 24);

const dateSlider = document.getElementById("dateSlider");
const yearSpan = document.getElementById("yearSpan");

// Set up the slider attributes
dateSlider.min = 2010;
dateSlider.max = 2024;//dayDifference;
dateSlider.value = 2024;

// Initialize date display
updateDateDisplay();

//get data
getData('/station_data').then((data) => {
    //dispose of existing prediction(s)
    loaderContainer.style.display = 'none'
    const station_data = data
    console.log(data)


    var [top, bottom, left, right] = getMapBounds();

    const selectedYear = getYear();
    displayStations(left, right, bottom, top, station_data, selectedYear);

    map.on("moveend", () => {
        const [top, bottom, left, right] = getMapBounds();
        const selectedYear = getYear();
    
        // Call displayStations with the updated date and map bounds
        displayStations(left, right, bottom, top, station_data, selectedYear);
    });
    loadCities(station_data);
    dateSlider.addEventListener("input", updateDateDisplay);
    dateSlider.addEventListener("input", () => {
        const [top, bottom, left, right] = getMapBounds();
        const selectedYear = getYear();
        loadCities(station_data);
        displayStations(left, right, bottom, top, station_data, selectedYear);       
    });
    

    document.getElementById('modelSend').addEventListener('click', () => {
        const [top, bottom, left, right] = getMapBounds();
        const selectedYear = getYear();
    
        // Filter by map bounds and date
        let filtered_station_data = station_data.filter(obj => {
            const openDate = parseDate(obj["Open Date"]);
            return (
                obj.Longitude >= left &&
                obj.Longitude <= right &&
                obj.Latitude >= bottom &&
                obj.Latitude <= top &&
                obj.Year <= selectedYear
            );
        });
    
        const keepKeys = ['Latitude', 'Longitude', 'Open Date'];
        filtered_station_data = filtered_station_data.map(obj => {
            const new_obj = {};
            keepKeys.forEach(e => new_obj[e] = obj[e]);
            return Object.values(new_obj);
        });
    
        console.log(filtered_station_data);
    
        fetch('/run_model', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filtered_station_data }),
        })
        .then(response => response.json())
        .then(data => {
            const zoom = map.getZoom();
            map.setZoom(zoom - 3);
    
            Object.entries(data).forEach(([algo, result]) => {
                L.circleMarker([+result[0], +result[1]], { radius: 10, renderer: myRenderer })
                    .setStyle({ color: 'green', fillColor: 'green' })
                    .addTo(map)
                    .bindPopup("Prediction: " + algo);
            });
        })
        .catch(error => console.error('Error:', error));
    });
});