import pandas as pd
from algos.frank import choose_new_location as frank_choose_new_location
from algos.noah_c import choose_new_location as noah_choose_new_location
from algos.noah_s import choose_new_location_kmeans 

def CreateOpenStationsfile(csv_file_path, parquet_file_path):
    # Read the CSV file
    df = pd.read_csv(csv_file_path)
    keep_cols = ['Groups With Access Code', 'Fuel Type Code', 'Station Name', 'Street Address', 'City', 'State', 'ZIP', 'Status Code'
                    , 'Latitude', 'Longitude', 'Open Date']
    df = df[keep_cols].dropna(how='any')

    df = df[(df['Status Code'] == 'E') & (df['Fuel Type Code'] == 'ELEC') & (df['Groups With Access Code'].str.contains('Public'))]
    df.drop(['Status Code', 'Fuel Type Code', 'Groups With Access Code'], axis=1, inplace=True)
    df['ZIP'] = df['ZIP'].astype(str)
    df['Year'] = df['Open Date'].apply(lambda x: int(x.split('-')[0]))
    df['Algorithm'] = 'Original'
    # Convert to Parquet file
    df.to_parquet(parquet_file_path, engine='fastparquet')
    print(f"OpenStations file has been created to {parquet_file_path}")
    
def GeneratePredictions(parquet_file_path, output_file_path):
    # Read the list of open stations
    df = pd.read_parquet(parquet_file_path)
    # Iterate over each row in the DataFrame and call the model to get the new location
    print(f"Total number of open stations: {len(df)}")
    print("Top 5 open stations:")
    print(df.head())
    # Create a DataFrame to store the predictions
    predictions = pd.DataFrame(columns=['Algorithm', 'Year', 'City', 'State', 'Latitude', 'Longitude'])
    for year in range(2010, 2024):
        df_year = df[df['Year'] < year]
        city_state_group = df_year.groupby(['City', 'State']).filter(lambda x: len(x) > 10).groupby(['City', 'State'])

        for (city, state), group in list(city_state_group):
            print(year, city, state)
            locations = list(group[['Latitude', 'Longitude']].itertuples(index=False, name=None))
            
            #Prediction 1
            new_location = frank_choose_new_location(locations)
            predictions = pd.concat([predictions, pd.DataFrame([{
                'Algorithm': 'Frank',
                'Year': year,
                'City': city,
                'State': state,
                'Latitude': new_location[0],
                'Longitude': new_location[1]
            }])], ignore_index=True)
            
            #Prediction 2
            new_location = noah_choose_new_location(locations)
            predictions = pd.concat([predictions, pd.DataFrame([{
                 'Algorithm': 'Noah_C',
                 'Year': year,
                 'City': city,
                 'State': state,
                 'Latitude': new_location[0],
                 'Longitude': new_location[1]
            }])], ignore_index=True)
            
            #Prediction 3
            new_location = choose_new_location_kmeans(locations)
            predictions = pd.concat([predictions, pd.DataFrame([{
                 'Algorithm': 'Noah_S',
                 'Year': year,
                 'City': city,
                 'State': state,
                 'Latitude': new_location[0],
                 'Longitude': new_location[1]
            }])], ignore_index=True)

    # Save the predictions DataFrame to a Parquet file
    predictions.to_parquet(output_file_path, engine='fastparquet')
    print(f"Predictions have been saved to {output_file_path}")

# Combine OpenStations and Predictions dataframes
def CombineDataFrames(openstations_file_path, predictions_file_path, combined_file_path):
    # Read the OpenStations and Predictions Parquet files
    openstations_df = pd.read_parquet(openstations_file_path)
    predictions_df = pd.read_parquet(predictions_file_path)

    # Merge the DataFrames on common columns
    combined_df = pd.merge(openstations_df, predictions_df, how='outer', on=['City', 'State', 'Latitude', 'Longitude','Year','Algorithm'])

    # Display the OpenStations DataFrame
    print("OpenStations DataFrame:")
    print(openstations_df.head())

    # Display the Predictions DataFrame
    print("Predictions DataFrame:")
    print(predictions_df.head())

    # Display the Combined DataFrame
    print("Combined DataFrame:")
    print(combined_df.head())


    # Save the combined DataFrame to a Parquet file
    combined_df.to_parquet(combined_file_path, engine='fastparquet')
    print(f"Combined data has been saved to {combined_file_path}")

# Do it
rawfile = 'data/alt_fuel_station.csv'
openstations = 'data/OpenStations.parquet'
predictions = 'data/Predictions.parquet'
CreateOpenStationsfile(rawfile, openstations)
GeneratePredictions(openstations, predictions)
CombineDataFrames(openstations, predictions, 'data/MapData.parquet')