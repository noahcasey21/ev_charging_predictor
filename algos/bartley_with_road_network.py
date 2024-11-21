import numpy as np
from geopy.distance import geodesic
from pulp import*
import osmnx
from shapely.geometry import Point, LineString

def get_nearest_road_dist(candidate,roads):
    """
    Calculates  the distance from the nearest road network for each proposed candidate location
    Parameters:
    - candidate ( tuple): Long and Lat of candidate location
    - roads ( Geoseries): Road network as Linestring geometries

    """
    candidate_cord = Point(candidate[1], candidate[0])
    return roads.distance(candidate_point).min() * 100  # Distance in Kilometers

def optimize_new_ev_station_location(existing_stations, ev_user_locations, user_densities, ev_ranges, grid_size=(10, 10), min_ev_users=40):
    """
    Optimize the location for a new EV charging station.

    Parameters:
    - existing_stations (list of tuples): Coordinates of existing stations as (latitude, longitude).
    - ev_user_locations (list of tuples): Coordinates of EV user clusters as (latitude, longitude).
    - user_densities (list of ints): Number of EV users for each cluster location.
    - ev_ranges (list of floats): EV range for each cluster location.
    - grid_size (tuple): Size of the grid for generating candidate locations.
    - min_ev_users (int): Minimum number of EV users required near the new station.

    Returns:
    - dict: Coordinates of the optimal new station location as {'Latitude': value, 'Longitude': value}.
    """
    
    # Calculate the average EV range
    ev_range = np.mean(ev_ranges)

    # Define grid boundaries based on the area around existing stations
    min_lat = min([loc[0] for loc in existing_stations]) - 0.5
    max_lat = max([loc[0] for loc in existing_stations]) + 0.5
    min_lon = min([loc[1] for loc in existing_stations]) - 0.5
    max_lon = max([loc[1] for loc in existing_stations]) + 0.5

    # Generate candidate locations on a grid within the defined area
    candidate_locations = []
    lat_range = np.linspace(min_lat, max_lat, grid_size[0])
    lon_range = np.linspace(min_lon, max_lon, grid_size[1])

    for lat in lat_range:
        for lon in lon_range:
            candidate_locations.append((lat, lon))

    # load in road newtwork using Open street map library
    G = osmnx.graph_from_bbox(max_lat, min_lat, max_lon, min_lon, network_type="drive")
    roads = ox.graph_to_gdfs(G, nodes=False, edges=True)["geometry"]

    # Initialize the optimization model
    model = LpProblem("Optimal_EV_Station_Location", LpMaximize)

    # Define decision variables for each candidate location
    x_vars = {}
    for i in range(len(candidate_locations)):
        x_vars[i] = LpVariable(f"x_{i}", cat="Binary")

    # Objective function: Maximize the distance to the nearest existing station
    objective = 0
    for i in range(len(candidate_locations)):
        distance_to_nearest_station = float("inf")
        for station in existing_stations:
            distance = geodesic(candidate_locations[i], station).km
            if distance < distance_to_nearest_station:
                distance_to_nearest_station = distance
        objective += x_vars[i] * distance_to_nearest_station
    model += objective, "Maximize_Distance_to_Nearest_Station"

    # Constraints
    for i, candidate in enumerate(candidate_locations):
        # Calculate distance to the nearest existing station
        distance_to_nearest_station = float("inf")
        for station in existing_stations:
            distance = geodesic(candidate, station).km
            if distance < distance_to_nearest_station:
                distance_to_nearest_station = distance
        
        # EV Range Constraint: Distance to nearest station should not exceed EV range
        model += distance_to_nearest_station * x_vars[i] <= ev_range

        # User Density Constraint: Ensure minimum EV user density
        user_density = 0
        for j, user_location in enumerate(ev_user_locations):
            if geodesic(candidate, user_location).km <= ev_range:
                user_density += user_densities[j]
        model += user_density * x_vars[i] >= min_ev_users

        # Road Proximity Constraint: Distance to the nearest road
        road_distance = get_nearest_road_distance(candidate, roads)
        if road_distance > max_distance_to_road:
            model += x_vars[i] == 0  # Adds constraint to the model to disqualify candidates too far from roads

    # Single Location Constraint: Only one new location can be selected
    model += lpSum(x_vars[i] for i in range(len(candidate_locations))) == 1

    # Solve the model
    model.solve()

    # Retrieve the coordinates of the best new location
    for i, point in enumerate(candidate_locations):
        if value(x_vars[i]) == 1:
            return {"Latitude": point[0], "Longitude": point[1]}
        else:
            # If no solution is found, return None
            return None

# Sample Data for Testing the Function
existing_stations = [
    (33.65, -84.42),
    (33.66, -84.44),
    (33.67, -84.41)
]

ev_user_locations = [
    (33.655, -84.423),
    (33.662, -84.430),
    (33.668, -84.417)
]

user_densities = [50, 70, 30]  # Number of EV users per user location
ev_ranges = [45, 50, 40]  # EV range for each user cluster in km

# Call the function with sample data
optimal_location = optimize_new_ev_station_location(existing_stations, ev_user_locations, user_densities, ev_ranges)
print("Optimal new station location based on sample data:", optimal_location)
