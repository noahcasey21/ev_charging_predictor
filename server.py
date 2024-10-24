from flask import Flask, Response, render_template, request, url_for
from flask_caching import Cache
from flask_compress import Compress
import pandas as pd
import orjson

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})
Compress(app)

@app.route('/', methods=['GET', 'POST'])
@cache.cached(timeout=300)
def index() -> None:
    result = False

    if request.method == 'POST':
        form = request.get_json()
        run_model(form)

    return render_template('main.html')


@app.route('/station_data', methods=['GET'])
@cache.cached(timeout=300)
def get_data() -> Response:
    df = pd.read_csv('data/alt_fuel_station.csv')
    keep_cols = ['Groups With Access Code', 'Fuel Type Code', 'Station Name', 'Street Address', 'City', 'State', 'ZIP', 'Status Code'
                 , 'Latitude', 'Longitude', 'Open Date']
    df = df[keep_cols].dropna(how='any')
    df = df[(df['Status Code'] == 'E') & (df['Fuel Type Code'] == 'ELEC') & (df['Groups With Access Code'].str.contains('Public'))].drop(['Status Code', 'Fuel Type Code', 'Groups With Access Code'], axis=1)
    json_data = orjson.dumps(df.to_dict(orient='records'))
    return Response(json_data, content_type='application/json')


@app.route('/run_model', methods=['GET', 'POST'])
def run_model() -> Response:
    '''
    Parameters:
    --------
    list_data: this is a list of lists where sublists have form [lat, long, open_date]
    
    Returns:
    -------
    List of latitudes and longitudes based on model calls
    '''
    #this will be a method that calls the model on given data
    #may format the return data to be used in webpage
    #post to local file that can be detected and run by javascript
    return request.json


if __name__ == "__main__":
    app.run(debug=True)