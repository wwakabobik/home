from flask import render_template

from db.queries import get_last_series_measurement
from pages.weather_station.tools import convert_param, convert_period


def single_data_page(table, period, param):
    fparam, meas_type = convert_param(param, table)
    num_period = convert_period(period)
    x, y = get_last_series_measurement(table=table, period=num_period, param=fparam, meas_type=meas_type)
    data = '<TABLE width=80% align="center" border="1px" cellspacing="0" cellpadding="2">'
    for i in range(len(x)):
        data = f'{data}<TR  valign="middle"><TD align="center">{x[i]}</TD><TD align="center">{y[i]}</TD></TR>'
    data = f'{data}</TABLE>'
    return render_template("weather_station/single_data_page.html",
                           param=param,
                           period=period,
                           data=data)
