#!/usr/bin/env python3.7

from datetime import datetime

from flask import Flask, jsonify, request, abort

from .db.db import init_app
from .db.weather_station import store_weather_data
from .pages.index import index_page
from .pages.weather_station.dashboard import dashboard_page
from .pages.weather_station.single_page import single_page
from .pages.weather_station.single_data_page import single_data_page
from .pages.weather_station.compare_page import compare_page
from .pages.weather_station.send_data import send_data


app = Flask(__name__, template_folder='templates')


@app.route('/api/v1/add_weather_data', methods=['POST'])
def store_in_db():
    if not request.json:
        abort(400)
    timestamp = str(datetime.now())
    data = request.json.get('data', "")
    db_data = f'"{timestamp}", {data}'
    store_weather_data(db_data)
    return jsonify({'data': db_data}), 201


@app.route('/send_data')
def send_weather_data():
    return send_data()


@app.route('/')
@app.route('/index')
def index():
    return index_page()


@app.route('/dashboard')
def dashboard():
    return dashboard_page()


@app.route('/single_page')
def single():
    period = request.args.get('period')
    param = request.args.get('param')
    return single_page(param=param, period=period)


@app.route('/single_page', methods=['POST'])
def single_via_post():
    period = request.form['period']
    param = request.form['param']
    return single_page(param=param, period=period)


@app.route('/single_data_page')
def single_data():
    period = request.args.get('period')
    param = request.args.get('param')
    return single_data_page(param=param, period=period)


@app.route('/compare_page', methods=['POST'])
def compare():
    period = request.form.get('period', None)
    param1 = request.form.get('param1', None)
    param2 = request.form.get('param2', None)
    return compare_page(param1=param1, param2=param2, period=period)


if __name__ == '__main__':
    init_app(app)
    app.run(debug=True, host='0.0.0.0', port='80')
