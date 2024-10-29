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
        L.circleMarker([station['Latitude'], station['Longitude']], {radius : 3, renderer : myRenderer})
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
    'zoomSnap': 0.5,
    'minZoom': 4,
    'maxZoom': 15
});

var myRenderer = L.canvas({ padding: 0.5 });

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

const loaderContainer = document.getElementById('loader-container');
//get data
getData('/station_data').then((data) => {
    //dispose of existing prediction(s)
    loaderContainer.style.display = 'none'
    const station_data = data
    //console.log(data)

    var [top, bottom, left, right] = getMapBounds();

    displayStations(left, right, bottom, top, station_data);

    map.on("moveend", function() {
        [top, bottom, left, right] = getMapBounds();
    
        displayStations(left, right, bottom, top, station_data);    
    })

    document.getElementById('modelSend').addEventListener('click', () => {

        [top, bottom, left, right] = getMapBounds();
        //filter locations
        var filtered_station_data = station_data.filter(obj =>
            obj.Longitude >= left && obj.Longitude <= right && obj.Latitude >= bottom && obj.Latitude <= top
        );

        const keepKeys = ['Latitude', 'Longitude', 'Open Date'];

        //filter keys and convert to array of arrays
        filtered_station_data = filtered_station_data.map(obj => {
            const new_obj = {};
            keepKeys.forEach(e => new_obj[e] = obj[e] );
            return Object.values(new_obj);
        });

        console.log(filtered_station_data)
        
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
        .then(data => {
            const zoom = map.getZoom()
            map.setZoom(zoom - 3)
            //structure: {"frank's algo" : [1, 2], ...}
            Object.entries(data).forEach(([algo, result]) => {
                console.log(algo);
                console.log(result);
                L.circleMarker([+result[0], +result[1]], {radius : 10, renderer : myRenderer})
                    .setStyle({color: 'green', fillColor: 'green'})
                    .addTo(map)
                    .bindPopup("Prediction: " + algo);
                });
        })
        .catch(error => console.error('Error:', error));
    });
});