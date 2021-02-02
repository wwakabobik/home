from flask import render_template

from pages.weather_station.tools import generate_scatter


def compare_page(param1, param2, period):
    if param1 is None:
        param1 = "temperature_in"
    if param2 is None:
        param2 = "temperature_in"
    if period is None:
        period = "day"
    offline_fig1 = generate_scatter(param=param1, period=period, width=600, height=600)
    offline_fig2 = generate_scatter(param=param2, period=period, width=600, height=600)
    return render_template("weather_station/compare_page.html",
                           param1=param1,
                           param2=param2,
                           period=period,
                           offline_fig1=offline_fig1,
                           offline_fig2=offline_fig2)
