from flask import render_template

from db.queries import get_last_measurement_pack, get_one_measurement


def power_page():
    power_data = get_last_measurement_pack('power_data', '0')
    wind_speed = get_one_measurement('wind_data', 'avg_kmh', '0')

    return render_template("power_management/power_dashboard.html",
                           avg_voltage=power_data['avg_voltage'],
                           avg_current=power_data['avg_current'],
                           avg_power=power_data['avg_power'],
                           avg_consumption=power_data['avg_consumption'],
                           wind_speed=wind_speed
                           )
