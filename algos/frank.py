import numpy as np
from geopy.distance import geodesic
import json


def choose_new_location(existing_locations, grid_size=(25, 25)):
    """
    Choose a new location using spatial queuing given a set of existing locations.

    Parameters:
    existing_locations (list of tuples): List of existing locations as (latitude, longitude) coordinates.
    grid_size (tuple): Size of the grid as (width, height).

    Returns:
    tuple: New location as (latitude, longitude) coordinates.
    """
    grid = np.zeros(grid_size)
    
    min_lat = min(loc[0] for loc in existing_locations)-1
    max_lat = max(loc[0] for loc in existing_locations)+1
    min_lon = min(loc[1] for loc in existing_locations)-1
    max_lon = max(loc[1] for loc in existing_locations)+1
    
    for loc in existing_locations:
        lat_idx = int((loc[0] - min_lat) * (grid_size[0] / (max_lat - min_lat)))
        lon_idx = int((loc[1] - min_lon) * (grid_size[1] / (max_lon - min_lon)))
        grid[lat_idx, lon_idx] = 1
    
    distances = np.zeros(grid_size)
    
    for lat_idx in range(grid_size[0]):
        for lon_idx in range(grid_size[1]):
            if grid[lat_idx, lon_idx] == 0:
                min_distance = float('inf')
                for loc in existing_locations:
                    grid_lat = lat_idx * (max_lat - min_lat) / grid_size[0] + min_lat
                    grid_lon = lon_idx * (max_lon - min_lon) / grid_size[1] + min_lon
                    distance = geodesic((grid_lat, grid_lon), loc).kilometers
                    if distance < min_distance:
                        min_distance = distance
                distances[lat_idx, lon_idx] = min_distance
    
    new_location_idx = np.unravel_index(np.argmax(distances), distances.shape)
    new_location = (new_location_idx[0] * (max_lat - min_lat) / grid_size[0] + min_lat, 
                    new_location_idx[1] * (max_lon - min_lon) / grid_size[1] + min_lon)
    return new_location

# SAMPLE existing_locations = [(37.7749, -122.4194), (34.0522, -118.2437), (40.7128, -74.0060)]
# Sample Payload
sPayload='{"filtered_station_data":[[33.653984,-84.397653,"2016-07-02"],[33.662898,-84.428118,"2016-10-07"],[33.653832,-84.423689,"2016-10-14"],[33.65972,-84.413647,"2018-06-14"],[33.658678,-84.42534,"2018-08-14"],[33.658015,-84.421226,"2018-08-16"],[33.653021,-84.430135,"2018-12-12"],[33.660132,-84.431519,"2017-07-17"],[33.657669,-84.421716,"2019-05-04"],[33.657737,-84.421292,"2019-05-04"],[33.653491,-84.450653,"2019-05-31"],[33.650656,-84.447945,"2020-03-01"],[33.65071,-84.448031,"2020-03-01"],[33.662897,-84.428088,"2021-01-27"],[33.653845,-84.423648,"2021-01-27"],[33.653822,-84.423798,"2021-01-27"],[33.653822,-84.424038,"2021-01-27"],[33.653831,-84.424175,"2021-01-27"],[33.65382,-84.423958,"2021-01-27"],[33.6538,-84.423757,"2021-01-27"],[33.65384,-84.424202,"2021-01-27"],[33.653824,-84.424014,"2021-01-27"],[33.653829,-84.424175,"2021-01-27"],[33.653826,-84.424105,"2021-01-27"],[33.653831,-84.424127,"2021-01-27"],[33.653813,-84.423891,"2021-01-27"],[33.653992,-84.397638,"2021-01-27"],[33.659613,-84.413669,"2021-01-27"],[33.658779,-84.425338,"2021-01-27"],[33.658774,-84.42532,"2021-01-27"],[33.658024,-84.421291,"2021-01-27"],[33.658031,-84.421083,"2021-01-27"],[33.653077,-84.430127,"2021-01-27"],[33.653128,-84.430123,"2021-01-27"],[33.657663,-84.421635,"2021-01-27"],[33.657721,-84.42103,"2021-01-27"],[33.657681,-84.421077,"2021-01-27"],[33.657645,-84.420498,"2021-01-27"],[33.657735,-84.420794,"2021-01-27"],[33.657762,-84.420826,"2021-01-27"],[33.657731,-84.421346,"2021-01-27"],[33.650603,-84.44786,"2021-01-27"],[33.650685,-84.447986,"2021-01-27"],[33.653863,-84.423704,"2021-07-31"],[33.657722,-84.421188,"2021-12-22"],[33.65647,-84.40343,"2022-02-22"],[33.656433,-84.40341,"2022-02-22"],[33.6594071,-84.4174653,"2020-04-10"],[33.657222,-84.431829,"2023-03-10"],[33.657198,-84.431872,"2023-03-10"],[33.657271,-84.431706,"2023-03-10"],[33.657252,-84.431743,"2023-03-10"],[33.657288,-84.431662,"2023-03-10"],[33.653034,-84.4507,"2023-04-16"],[33.653022,-84.450828,"2024-06-07"],[33.653038,-84.450817,"2024-06-14"]]}'
# Parse the JSON payload
data = json.loads(sPayload)

# Extract the coordinates from the payload
existing_locations = [(entry[0], entry[1]) for entry in data['filtered_station_data']]
new_location = choose_new_location(existing_locations)
new_location_json = json.dumps({"new_location": new_location})
print(new_location_json)