import json
import time
import numpy as np
from sklearn.cluster import KMeans
from geopy.distance import geodesic

def choose_new_location_kmeans(existing_locations, n_clusters=10, void_threshold_km=10.0):
    """
    Choose a new location using K-means clustering with void detection.
    Voids are coverage gaps in the coordinate grid.
    Void detection involves finding large areas between clusters that exceed some minimum distance threshold.
    
    Parameters:
    existing_locations (list of tuples): List of existing locations as (latitude, longitude) coordinates.
    n_clusters (int): Number of clusters to form.
    void_threshold_km (float): Minimum distance in kilometers to consider an area as a void.
    
    Returns:
    tuple: New location as (latitude, longitude) coordinates.
    """
    locations_array = np.array(existing_locations)
    
    kmeans = KMeans(n_clusters=n_clusters, n_init="auto", random_state=0)
    kmeans.fit(locations_array)
    
    cluster_centers = kmeans.cluster_centers_
    
    # create grid of potential points
    min_lat = min(loc[0] for loc in existing_locations) - 0.1
    max_lat = max(loc[0] for loc in existing_locations) + 0.1
    min_lon = min(loc[1] for loc in existing_locations) - 0.1
    max_lon = max(loc[1] for loc in existing_locations) + 0.1
    
    grid_size = 50
    lat_grid = np.linspace(min_lat, max_lat, grid_size)
    lon_grid = np.linspace(min_lon, max_lon, grid_size)
    
    # create mesh grid for potential locations
    lat_mesh, lon_mesh = np.meshgrid(lat_grid, lon_grid)
    potential_points = np.column_stack((lat_mesh.ravel(), lon_mesh.ravel()))
    
    # calculate distances to nearest existing station for each potential point
    void_scores = np.zeros(len(potential_points))
    
    for i, point in enumerate(potential_points):
        # distance to nearest existing station
        min_station_dist = min(geodesic(point, loc).kilometers for loc in existing_locations)
        # distance to nearest cluster center
        min_cluster_dist = min(geodesic(point, center).kilometers for center in cluster_centers)
        
        # calculate void score (higher score = better candidate)
        #   min_station_dist: higher value is better because we want to place new stations far from existing ones
        #       this is the primary factor for identifying voids
        #       linear scale
        #   min_cluster_dist inverse: lower value is better because we want to stay relatively close to population centers (demand areas)
        #       nonlinear scale - diminishing returns as distance increases
        if min_station_dist > void_threshold_km:
            void_scores[i] = min_station_dist * (1 / (min_cluster_dist + 1))
        else:
            void_scores[i] = 0
            
    # find the point with the highest void score
    best_point_idx = np.argmax(void_scores)
    new_location = tuple(potential_points[best_point_idx])
    
    return new_location

def analyze_coverage(existing_locations, new_location):
    """
    Analyze the coverage improvement with the new location.
    
    Parameters:
    existing_locations (list of tuples): List of existing locations.
    new_location (tuple): New station location.
    
    Returns:
    dict: Coverage analysis metrics.
    """
    all_locations = existing_locations + [new_location]
    
    # calculate average distance to nearest station before and after
    grid_size = 20
    min_lat = min(loc[0] for loc in all_locations) - 0.1
    max_lat = max(loc[0] for loc in all_locations) + 0.1
    min_lon = min(loc[1] for loc in all_locations) - 0.1
    max_lon = max(loc[1] for loc in all_locations) + 0.1
    
    lat_grid = np.linspace(min_lat, max_lat, grid_size)
    lon_grid = np.linspace(min_lon, max_lon, grid_size)
    grid_points = [(lat, lon) for lat in lat_grid for lon in lon_grid]
    
    # calculate coverage metrics before and after new station
    old_distances = []
    new_distances = []
    for point in grid_points:
        old_min_dist = min(geodesic(point, loc).kilometers for loc in existing_locations)
        new_min_dist = min(geodesic(point, loc).kilometers for loc in all_locations)
        old_distances.append(old_min_dist)
        new_distances.append(new_min_dist)
    
    return {
        "avg_distance_before": np.mean(old_distances),
        "avg_distance_after": np.mean(new_distances),
        "max_distance_before": max(old_distances),
        "max_distance_after": max(new_distances),
        "coverage_improvement_percent": (np.mean(old_distances) - np.mean(new_distances)) / np.mean(old_distances) * 100
    }


if __name__ == "__main__":
    sample_payload = '{"filtered_station_data":[[33.653984,-84.397653,"2016-07-02"],[33.662898,-84.428118,"2016-10-07"],[33.653832,-84.423689,"2016-10-14"],[33.65972,-84.413647,"2018-06-14"],[33.658678,-84.42534,"2018-08-14"],[33.658015,-84.421226,"2018-08-16"],[33.653021,-84.430135,"2018-12-12"],[33.660132,-84.431519,"2017-07-17"],[33.657669,-84.421716,"2019-05-04"],[33.657737,-84.421292,"2019-05-04"],[33.653491,-84.450653,"2019-05-31"],[33.650656,-84.447945,"2020-03-01"],[33.65071,-84.448031,"2020-03-01"],[33.662897,-84.428088,"2021-01-27"],[33.653845,-84.423648,"2021-01-27"],[33.653822,-84.423798,"2021-01-27"],[33.653822,-84.424038,"2021-01-27"],[33.653831,-84.424175,"2021-01-27"],[33.65382,-84.423958,"2021-01-27"],[33.6538,-84.423757,"2021-01-27"],[33.65384,-84.424202,"2021-01-27"],[33.653824,-84.424014,"2021-01-27"],[33.653829,-84.424175,"2021-01-27"],[33.653826,-84.424105,"2021-01-27"],[33.653831,-84.424127,"2021-01-27"],[33.653813,-84.423891,"2021-01-27"],[33.653992,-84.397638,"2021-01-27"],[33.659613,-84.413669,"2021-01-27"],[33.658779,-84.425338,"2021-01-27"],[33.658774,-84.42532,"2021-01-27"],[33.658024,-84.421291,"2021-01-27"],[33.658031,-84.421083,"2021-01-27"],[33.653077,-84.430127,"2021-01-27"],[33.653128,-84.430123,"2021-01-27"],[33.657663,-84.421635,"2021-01-27"],[33.657721,-84.42103,"2021-01-27"],[33.657681,-84.421077,"2021-01-27"],[33.657645,-84.420498,"2021-01-27"],[33.657735,-84.420794,"2021-01-27"],[33.657762,-84.420826,"2021-01-27"],[33.657731,-84.421346,"2021-01-27"],[33.650603,-84.44786,"2021-01-27"],[33.650685,-84.447986,"2021-01-27"],[33.653863,-84.423704,"2021-07-31"],[33.657722,-84.421188,"2021-12-22"],[33.65647,-84.40343,"2022-02-22"],[33.656433,-84.40341,"2022-02-22"],[33.6594071,-84.4174653,"2020-04-10"],[33.657222,-84.431829,"2023-03-10"],[33.657198,-84.431872,"2023-03-10"],[33.657271,-84.431706,"2023-03-10"],[33.657252,-84.431743,"2023-03-10"],[33.657288,-84.431662,"2023-03-10"],[33.653034,-84.4507,"2023-04-16"],[33.653022,-84.450828,"2024-06-07"],[33.653038,-84.450817,"2024-06-14"]]}'
    data = json.loads(sample_payload)
    
    # extract latitute and longitude coordinates from the payload
    existing_locations = [(coordinate[0], coordinate[1]) for coordinate in data["filtered_station_data"]]
    
    s = time.time()
    new_location = choose_new_location_kmeans(existing_locations)
    coverage_analysis = analyze_coverage(existing_locations, new_location)
    e = time.time()
    print(f"K-means clustering with void detection took {e-s} seconds")
    
    response = {
        "new_location": new_location,
        "coverage_analysis": coverage_analysis
    }
    print(json.dumps(response, indent=4))
