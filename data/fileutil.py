import pandas as pd

# Read the CSV file
csv_file_path = 'data/alt_fuel_station.csv'
df = pd.read_csv(csv_file_path)
keep_cols = ['Groups With Access Code', 'Fuel Type Code', 'Station Name', 'Street Address', 'City', 'State', 'ZIP', 'Status Code'
                , 'Latitude', 'Longitude', 'Open Date']
df = df[keep_cols].dropna(how='any')

df = df[(df['Status Code'] == 'E') & (df['Fuel Type Code'] == 'ELEC') & (df['Groups With Access Code'].str.contains('Public'))]
df.drop(['Status Code', 'Fuel Type Code', 'Groups With Access Code'], axis=1, inplace=True)
df['ZIP'] = df['ZIP'].astype(str)

# Convert to Parquet file
parquet_file_path = 'data/alt_fuel_station.parquet'
df.to_parquet(parquet_file_path, engine='fastparquet')
print(f"CSV file has been converted to Parquet file at {parquet_file_path}")