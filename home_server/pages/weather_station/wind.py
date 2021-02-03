from flask import render_template

from db.queries import get_last_measurement_pack


def wind_page():
    wind_data = get_last_measurement_pack('wind_data', '0')

    return render_template("weather_station/wind_dashboard.html",
                           avg_rps=wind_data['avg_rps'],
                           max_rps=wind_data['max_rps'],
                           min_rps=wind_data['min_rps'],
                           avg_ms=wind_data['avg_ms'],
                           max_ms=wind_data['max_ms'],
                           min_ms=wind_data['min_ms'],
                           avg_kmh=wind_data['avg_kmh'],
                           max_kmh=wind_data['max_kmh'],
                           min_kmh=wind_data['min_kmh'],
                           avg_knots=wind_data['avg_knots'],
                           max_knots=wind_data['max_knots'],
                           min_knots=wind_data['min_knots'],
                           heading=wind_data['heading'],
                           heading_abbr=wind_data['heading_abbr']
                           )
