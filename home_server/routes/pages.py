from pages.index import index_page
from pages.weather_station.dashboard import dashboard_page
from page.weather_station.wind import wind_page
from page.power_management.power import power_page


@app.route('/')
@app.route('/index')
def index():
    return index_page()


@app.route('/dashboard')
def dashboard():
    return dashboard_page()


@app.route('/wind')
def wind():
    return wind_page()


@app.route('/power')
def power():
    return power_page()
