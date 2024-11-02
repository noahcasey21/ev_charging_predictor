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
    
    min_lat = min(loc[0] for loc in existing_locations)
    max_lat = max(loc[0] for loc in existing_locations)
    min_lon = min(loc[1] for loc in existing_locations)
    max_lon = max(loc[1] for loc in existing_locations)
    
    for loc in existing_locations:
        lat_idx = int((loc[0] - min_lat) * (grid_size[0] / (max_lat - min_lat)))-1
        lon_idx = int((loc[1] - min_lon) * (grid_size[1] / (max_lon - min_lon)))-1
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
    new_location = ((new_location_idx[0]+1) * (max_lat - min_lat) / grid_size[0] + min_lat, 
                    (new_location_idx[1]+1) * (max_lon - min_lon) / grid_size[1] + min_lon)
    return new_location

# # SAMPLE existing_locations = [(37.7749, -122.4194), (34.0522, -118.2437), (40.7128, -74.0060)]
# # Sample Payload
#sPayload='{"filtered_station_data":[[33.566938,-84.344405,"2011-03-15"],[33.561906,-84.344267,"2016-11-01"],[33.575905,-84.34529,"2019-08-16"],[33.554255,-84.36992,"2021-09-24"],[33.55424,-84.369884,"2021-09-24"],[33.575596,-84.413376,"2022-06-23"],[33.575577,-84.41337,"2022-06-23"],[33.549994,-84.41643,"2022-07-27"],[33.582536,-84.378756,"2022-09-21"],[33.5761017,-84.3548001,"2023-04-13"],[33.56839,-84.318583,"2024-02-15"],[33.55998,-84.344854,"2024-08-31"]]}'
# # Parse the JSON payload
#data = json.loads(sPayload)

# # Extract the coordinates from the payload
# existing_locations = [(entry[0], entry[1]) for entry in data['filtered_station_data']]
# new_location = choose_new_location(existing_locations)
# new_location_json = json.dumps({"new_location": new_location})
# print(new_location_json)