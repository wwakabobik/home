from datetime import datetime
from time import time

from flask import jsonify, request, abort

from db.queries import store_weather_data
from pages.weather_station.send_data import send_data, send_data_to_informer


@app.route('/api/v1/send_data')
def send_weather_data():
    return send_data()


@app.route('/api/v1/add_weather_data', methods=['POST'])
def store_weather_data():
    if not request.json:
        abort(400)
    timestamp = str(datetime.now())
    unix_timestamp = int(time())
    data = request.json.get('data', "")
    db_data = f'"{timestamp}", {unix_timestamp}, {data}'
    store_weather_data(db_data)
    return jsonify({'data': db_data}), 201


@app.route('/api/v1/add_power_data', methods=['POST'])
def store_power_data():
    if not request.json:
        abort(400)
    timestamp = str(datetime.now())
    unix_timestamp = int(time())
    data = request.json.get('data', "")[2:]
    db_data = f'"{timestamp}", {unix_timestamp}, {data}'
    store_power_data(db_data)
    return jsonify({'data': db_data}), 201


@app.route('/api/v1/add_wind_data', methods=['POST'])
def store_wind_data():
    if not request.json:
        abort(400)
    timestamp = str(datetime.now())
    unix_timestamp = int(time())
    data = request.json.get('data', "")[2:]
    db_data = f'"{timestamp}", {unix_timestamp}, {data}'
    store_wind_data(db_data)
    return jsonify({'data': db_data}), 201


@app.route('/api/v1/get_weather_data', methods=['GET'])
def store_wind_data():
    return send_data_to_informer()
