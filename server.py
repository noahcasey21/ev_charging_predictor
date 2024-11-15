from flask import Flask, Response, render_template, request, url_for
from flask_caching import Cache
from flask_compress import Compress
import pandas as pd
import orjson
import json
from algos.frank import choose_new_location as frank_choose_new_location
from algos.noah_c import choose_new_location as noah_choose_new_location
from algos.noah_s import choose_new_location_kmeans 

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
    df = pd.read_parquet('data/alt_fuel_station.parquet')
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
    #post to local file that can be detected and run by javascript
    data = request.json['filtered_station_data']
    existing_locations = [(entry[0], entry[1]) for entry in data]

    frank_pred = frank_choose_new_location(existing_locations)
    noah_c_pred = noah_choose_new_location(existing_locations)
    noah_s_pred = choose_new_location_kmeans(existing_locations)

    predictions = {
        'Frank' : [round(float(frank_pred[0]), 5), round(float(frank_pred[1]), 5)],
        'Noah C' : [round(float(noah_c_pred[0]), 5), round(float(noah_c_pred[1]), 5)],
        'Noah S' : [round(float(noah_s_pred[0]), 5), round(float(noah_s_pred[1]), 5)]
        }
    
    pred_json = orjson.dumps(predictions)
    return Response(pred_json, content_type='application/json')


if __name__ == "__main__":
    app.run(debug=True)