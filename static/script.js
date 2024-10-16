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

function displayStations(leftLong, rightLong, bottomLat, topLat, station_data) {
    var filtered_station_data = station_data.filter(obj =>
        obj.Longitude >= leftLong && obj.Longitude <= rightLong && obj.Latitude >= bottomLat && obj.Latitude <= topLat
    );

    //boomer loop
    for (var i = 0; i < filtered_station_data.length; i++) {
        var station = filtered_station_data[i]
        L.marker([station['Latitude'], station['Longitude']])
            .addTo(map)
            .bindPopup(station['Station Name'] + '<br>' + station['Street Address']
                + '<br>' + station.City + ', ' + station.State
            );
    }
}

var maxBounds = [
    [24.396308, -125.000000], // Southwest corner
    [49.384358, -66.934570]   // Northeast corner
]

var map = L.map('map', {
    'center': [33.77, -84.40],
    'zoom': 10,
    'maxBounds': maxBounds,
    'zoomSnap': 0.25,
    'minZoom': 4,
    'maxZoom': 15
});

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

const loaderContainer = document.getElementById('loader-container');
//get data
getData('/station_data').then((data) => {
    loaderContainer.style.display = 'none'
    const station_data = data
    console.log(data)

    var [top, bottom, left, right] = getMapBounds();

    displayStations(left, right, bottom, top, station_data);

    map.on("moveend", function() {
        [top, bottom, left, right] = getMapBounds();
    
        displayStations(left, right, bottom, top, station_data);    
    })

    document.getElementById('modelSend').addEventListener('click', () => {

        [top, bottom, left, right] = getMapBounds();
        var filtered_station_data = station_data.filter(obj =>
            obj.Longitude >= leftLong && obj.Longitude <= rightLong && obj.Latitude >= bottomLat && obj.Latitude <= topLat
        );

        fetch('/run_model', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                filtered_station_data
            }),
        })
        .then(response => response.json())
        .then(data => console.log('Response:', data)) //this is where we post our prediction
        .catch(error => console.error('Error:', error));
    });
});