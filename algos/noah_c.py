from geopy.distance import geodesic

def choose_new_location(existing_locations : list[list]) -> tuple:
    """
    Choose a new location using state of charge approximation along vertical and horizontal lines to emulate highways.

    Parameters:
    existing_locations (list of lists): List of existing locations as (latitude, longitude) coordinates.

    Returns:
    tuple: New location as (latitude, longitude) coordinates.
    """

    def get_indices(value : float, _list : list) -> list:
        result = []
        for i in range(len(_list)):
            if value == _list[i]:
                result.append(i)

        return result

    #how many miles range EV has on average (rounded down) in miles approx converted to lat long
    STATE_OF_CHARGE = 25 / (24901.92 / 360)
    ROADS = 10 #fit 10 vertical and 10 horizontal lines

    lats = [i[0] for i in existing_locations]
    longs = [i[1] for i in existing_locations]

    min_lat = min(lats)
    max_lat = max(lats)
    min_long = min(longs)
    max_long = max(longs)
    lat_step = (max_lat - min_lat) / (ROADS - 1)
    long_step = (max_long - min_long) / (ROADS - 1)

    lat_lines = [min_lat + n * lat_step for n in range(ROADS)]
    long_lines = [min_long + n * long_step for n in range(ROADS)]

    lat_assign = [0] * ROADS
    long_assign = [0] * ROADS

    #iterate and assign
    PSEUDO_LAT_STEP = lat_step / 2
    PSEUDO_LONG_STEP = long_step / 2
    for lat, long in existing_locations:
        lat_assigned = False
        long_assigned = False
        i = 0
        while i < ROADS:
            #check lat
            if not lat_assigned and (lat_lines[i] + PSEUDO_LAT_STEP >= lat) and (lat_lines[i] - PSEUDO_LAT_STEP <= lat):
                lat_assign[i] += 1
                lat_assigned = True
            #check long
            if not long_assigned and (long_lines[i] + PSEUDO_LONG_STEP >= long) and (long_lines[i] - PSEUDO_LONG_STEP <= long):
                long_assign[i] += 1 
                long_assigned = True

            i += 1

    #we now have the most likely highway/major road values
    best_lat = max(lat_assign)
    best_lat_roads = get_indices(best_lat, lat_assign)
    best_long = max(long_assign)
    best_long_roads = get_indices(best_long, long_assign)

    if best_lat > best_long:
        lat = True 
    elif best_lat <= best_long:
        lat = False

    roads = best_lat_roads if lat else best_long_roads

    #deal with ties: reassign numbers by splitting locations again, if another tie, choose first
    # if len(roads) > 1:

    #     road = 
    # else:
    #     road = roads[0]
    road = lat_lines[roads[0]] if lat else long_lines[roads[0]]
    #get min and max in line and add/subtract value away from grouping
    if lat:
        sep = max_long - (max_long - min_long)
    else:
        sep = max_lat - (max_lat - min_lat)

    #choose side with lower grouping
    j = 0 if lat else 1
    vals = [0, 0] #[lower, upper]
    for loc in existing_locations:
        if loc[j] < sep:
            vals[0] += 1
        else:
            vals[1] += 1
    side = 0 if vals[0] < vals[1] else 1
    
    _end = max(existing_locations[0][0], existing_locations[0][1])
    PSEUDO_STEP = PSEUDO_LAT_STEP if lat else PSEUDO_LONG_STEP
    for loc in existing_locations:
        if loc[j] <= road + PSEUDO_STEP and loc[j] >= road - PSEUDO_STEP:
            if side == 0 and loc[j] < _end:
                _end = loc[j]
            elif side == 1 and loc[j] > _end:
                _end = loc[j]
 
    latitude = road if lat else _end + STATE_OF_CHARGE
    longitude = _end + STATE_OF_CHARGE if lat else road
    return (latitude, longitude)


def test_choose() -> tuple:
    test_data = [[33.653984,-84.397653,"2016-07-02"],[33.662898,-84.428118,"2016-10-07"],[33.653832,-84.423689,"2016-10-14"],[33.65972,-84.413647,"2018-06-14"],[33.658678,-84.42534,"2018-08-14"],[33.658015,-84.421226,"2018-08-16"],[33.653021,-84.430135,"2018-12-12"],[33.660132,-84.431519,"2017-07-17"],[33.657669,-84.421716,"2019-05-04"],[33.657737,-84.421292,"2019-05-04"],[33.653491,-84.450653,"2019-05-31"],[33.650656,-84.447945,"2020-03-01"],[33.65071,-84.448031,"2020-03-01"],[33.662897,-84.428088,"2021-01-27"],[33.653845,-84.423648,"2021-01-27"],[33.653822,-84.423798,"2021-01-27"],[33.653822,-84.424038,"2021-01-27"],[33.653831,-84.424175,"2021-01-27"],[33.65382,-84.423958,"2021-01-27"],[33.6538,-84.423757,"2021-01-27"],[33.65384,-84.424202,"2021-01-27"],[33.653824,-84.424014,"2021-01-27"],[33.653829,-84.424175,"2021-01-27"],[33.653826,-84.424105,"2021-01-27"],[33.653831,-84.424127,"2021-01-27"],[33.653813,-84.423891,"2021-01-27"],[33.653992,-84.397638,"2021-01-27"],[33.659613,-84.413669,"2021-01-27"],[33.658779,-84.425338,"2021-01-27"],[33.658774,-84.42532,"2021-01-27"],[33.658024,-84.421291,"2021-01-27"],[33.658031,-84.421083,"2021-01-27"],[33.653077,-84.430127,"2021-01-27"],[33.653128,-84.430123,"2021-01-27"],[33.657663,-84.421635,"2021-01-27"],[33.657721,-84.42103,"2021-01-27"],[33.657681,-84.421077,"2021-01-27"],[33.657645,-84.420498,"2021-01-27"],[33.657735,-84.420794,"2021-01-27"],[33.657762,-84.420826,"2021-01-27"],[33.657731,-84.421346,"2021-01-27"],[33.650603,-84.44786,"2021-01-27"],[33.650685,-84.447986,"2021-01-27"],[33.653863,-84.423704,"2021-07-31"],[33.657722,-84.421188,"2021-12-22"],[33.65647,-84.40343,"2022-02-22"],[33.656433,-84.40341,"2022-02-22"],[33.6594071,-84.4174653,"2020-04-10"],[33.657222,-84.431829,"2023-03-10"],[33.657198,-84.431872,"2023-03-10"],[33.657271,-84.431706,"2023-03-10"],[33.657252,-84.431743,"2023-03-10"],[33.657288,-84.431662,"2023-03-10"],[33.653034,-84.4507,"2023-04-16"],[33.653022,-84.450828,"2024-06-07"],[33.653038,-84.450817,"2024-06-14"]]
    test_data = [[l[0], l[1]] for l in test_data]

    return choose_new_location(test_data)


#print(test_choose())#comment out in production