from flask import render_template

from pages.weather_station.tools import generate_scatter


def single_weather_page(param, period):
    offline_fig = generate_scatter(table='weather_data', param=param, period=period)
    return render_template("weather_station/single_weather_page.html",
                           param=param,
                           period=period,
                           offline_fig=offline_fig)


def single_wind_page(param, period):
    offline_fig = generate_scatter(table='wind_data', param=param, period=period)
    return render_template("weather_station/single_wind_page.html",
                           param=param,
                           period=period,
                           offline_fig=offline_fig)


def single_power_page(param, period):
    offline_fig = generate_scatter(table='power_data', param=param, period=period)
    return render_template("weather_station/single_power_page.html",
                           param=param,
                           period=period,
                           offline_fig=offline_fig)
