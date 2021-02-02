from flask import render_template

from pages.weather_station.tools import generate_scatter


def single_page(param, period):
    offline_fig = generate_scatter(param=param, period=period)
    return render_template("weather_station/single_page.html",
                           param=param,
                           period=period,
                           offline_fig=offline_fig)
