import pandas as pd
import numpy as np

def haversine(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    r = 3958.8
    return c * r

def CreateExperiments(station_data_path, predictions_path, write_path):
    station_data = pd.read_parquet(station_data_path)
    predictions = pd.read_parquet(predictions_path)

    #coalse preds
    predictions['Lat'] = predictions['Latitude'].fillna(predictions['New_Latitude'])    
    predictions['Long'] = predictions['Longitude'].fillna(predictions['New_Longitude'])

    #first created location in a year
    first_location = station_data.loc[station_data.groupby(['City', 'State', 'Year'])['Open Date'].idxmin()].reset_index(drop=True)
    #create the year offset
    first_location['Year'] = first_location['Year'] - 1
    
    #join in predictions
    experiment = pd.merge(predictions, first_location, how='left', left_on=['City', 'State', 'Year'], right_on=['City', 'State', 'Year'], suffixes=('_l', '_r'))

    #setup how we need
    experiment['Distance'] = haversine(experiment['Lat'], experiment['Long'], experiment['Latitude_r'], experiment['Longitude_r'])
    experiment = experiment[['City', 'State', 'Year', 'Algorithm_l', 'Distance']].dropna()

    experiment.to_parquet(write_path, engine='fastparquet')


CreateExperiments('data/OpenStations.parquet', 'data/predictions.parquet', 'data/experiment.parquet')