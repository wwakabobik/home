import math

from plotly import graph_objects, offline

from db.weather_station import data_update_period, get_last_series_measurement


units = {'temperature': '°C', 'humidity': '%', 'pressure': 'mm Hg', 'dew_point': '°C'}


def convert_period(period):
    if period == "hour":
        num_period = int(60);
    elif period == "day":
        num_period = int(60 * 24)
    elif period == "week":
        num_period = int(60 * 24 * 7)
    elif period == "month":
        num_period = int(60 * 24 * 30)
    elif period == "year":
        num_period = int(60 * 24 * 365)
    else:
        raise Exception('Wrong period', f'{period}')
    return num_period


def convert_param(param):
    if "_in" in param:
        meas_type = 0
        fparam = param[:-3]
    elif "_out" in param:
        meas_type = 1
        fparam = param[:-4]
    else:
        meas_type=0
        fparam=param
    return fparam, meas_type


def generate_scatter(param, period, height=None, width=None):
    fparam, meas_type = convert_param(param)
    num_period = convert_period(period)
    x, y = get_last_series_measurement(period=num_period, param=fparam, meas_type=meas_type)
    line_chart1 = graph_objects.Scatter(x=x, y=y)
    lay1 = graph_objects.Layout(
        title=f'{param}',
        yaxis=dict(title=f'{units[fparam]}', ticks=f'inside'),
        height=height,
        width=width
    )
    fig1 = graph_objects.Figure(data=line_chart1, layout=lay1)
    offline_fig = offline.plot(fig1,
                               config={"displayModeBar": False},
                               show_link=False,
                               include_plotlyjs=True,
                               output_type='div')
    return offline_fig


def celsius_to_fahrenheit(celsius):
    farenheit = 9.0 / 5.0 * float(celsius) + 32
    return farenheit


def fahrenheit_to_celsius(farenheit):
    celsius = round(((farenheit - 32) * 5/9), 2)
    return celsius


def mmhg_to_baromin(mmhg):
    return float(mmhg)/25.4


def heat_index(temp, hum):
    fahrenheit = celsius_to_fahrenheit(temp)
    # Creating multiples of 'fahrenheit' & 'hum' values for the coefficients
    T2 = pow(fahrenheit, 2)
    T3 = pow(fahrenheit, 3)
    H2 = pow(hum, 2)
    H3 = pow(hum, 3)

    # Coefficients for the calculations
    C1 = [-42.379, 2.04901523, 10.14333127, -0.22475541, -6.83783e-03, -5.481717e-02, 1.22874e-03, 8.5282e-04,
          -1.99e-06]
    C2 = [0.363445176, 0.988622465, 4.777114035, -0.114037667, -0.000850208, -0.020716198, 0.000687678, 0.000274954, 0]
    C3 = [16.923, 0.185212, 5.37941, -0.100254, 0.00941695, 0.00728898, 0.000345372, -0.000814971, 0.0000102102,
          -0.000038646, 0.0000291583, 0.00000142721, 0.000000197483, -0.0000000218429, 0.000000000843296,
          -0.0000000000481975]

    # Calculating heat-indexes with 3 different formula
    heatindex1 = C1[0] + (C1[1] * fahrenheit) + (C1[2] * hum) + (C1[3] * fahrenheit * hum) + (C1[4] * T2) + (
                C1[5] * H2) + (C1[6] * T2 * hum) + (C1[7] * fahrenheit * H2) + (C1[8] * T2 * H2)
    heatindex2 = C2[0] + (C2[1] * fahrenheit) + (C2[2] * hum) + (C2[3] * fahrenheit * hum) + (C2[4] * T2) + (
                C2[5] * H2) + (C2[6] * T2 * hum) + (C2[7] * fahrenheit * H2) + (C2[8] * T2 * H2)
    heatindex3 = C3[0] + (C3[1] * fahrenheit) + (C3[2] * hum) + (C3[3] * fahrenheit * hum) + (C3[4] * T2) + (
                C3[5] * H2) + (C3[6] * T2 * hum) + (C3[7] * fahrenheit * H2) + (C3[8] * T2 * H2) + (C3[9] * T3) + (
                             C3[10] * H3) + (C3[11] * T3 * hum) + (C3[12] * fahrenheit * H3) + (C3[13] * T3 * H2) + (
                             C3[14] * T2 * H3) + (C3[15] * T3 * H3)

    avg_heat_index = (heatindex1 + heatindex2 + heatindex3)/3.0
    return avg_heat_index


def humidex(t, d):
    kelvin = 273.15
    temperature = t + kelvin
    dewpoint = d + kelvin

    # Calculate vapor pressure in mbar.
    e = 6.11 * math.exp(5417.7530 * ((1 / kelvin) - (1 / dewpoint)))

    # Calculate saturation vapor pressure
    h = 0.5555 * (e - 10.0)

    humidex = temperature + h - kelvin

    return humidex
