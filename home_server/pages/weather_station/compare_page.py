from flask import render_template

from pages.shared.tools import generate_scatter


def compare_page(table1, table2, param1, param2, period):
    if param1 is None:
        param1 = "temperature_in"
    if param2 is None:
        param2 = "temperature_in"
    if period is None:
        period = "day"
    offline_fig1 = generate_scatter(table1=table1, param=param1, period=period, width=600, height=600)
    offline_fig2 = generate_scatter(table2=table2, param=param2, period=period, width=600, height=600)
    return render_template("weather_station/compare_page.html",
                           param1=param1,
                           param2=param2,
                           period=period,
                           offline_fig1=offline_fig1,
                           offline_fig2=offline_fig2)
