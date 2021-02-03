from flask import request

from pages.shared.single_page import single_weather_page, single_wind_page, single_power_page
from pages.shared.single_data_page import single_data_page
from pages.weather_station.compare_page import compare_page


@app.route('/single_weather_page')
def single_weather_page_via_url():
    period = request.args.get('period')
    param = request.args.get('param')
    return single_weather_page(param=param, period=period)


@app.route('/single_wind_page')
def single_wind_page_via_url():
    period = request.args.get('period')
    param = request.args.get('param')
    return single_weather_page(param=param, period=period)


@app.route('/single_power_page')
def single_power_page_via_url():
    period = request.args.get('period')
    param = request.args.get('param')
    return single_weather_page(param=param, period=period)


@app.route('/single_weather_page', methods=['POST'])
def single_weather_page_via_post():
    period = request.form['period']
    param = request.form['param']
    return single_weather_page(param=param, period=period)


@app.route('/single_wind_page', methods=['POST'])
def single_wind_page_via_post():
    period = request.form['period']
    param = request.form['param']
    return single_wind_page(param=param, period=period)


@app.route('/single_power_page', methods=['POST'])
def single_power_page_via_post():
    period = request.form['period']
    param = request.form['param']
    return single_power_page(param=param, period=period)


@app.route('/single_data_page')
def single_data():
    table = request.args.get('table')
    period = request.args.get('period')
    param = request.args.get('param')
    return single_data_page(table=table, param=param, period=period)


@app.route('/compare_page', methods=['POST'])
def compare():
    period = request.form.get('period', None)
    param1 = request.form.get('param1', None)
    param2 = request.form.get('param2', None)
    return compare_page(param1=param1, param2=param2, period=period)
