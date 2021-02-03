from flask import render_template
from wunderground_pws import WUndergroundAPI, units

from db.queries import get_one_measurement, data_update_period, get_last_measurement_pack
from pages.shared.tools import deg_to_heading
from secure_data import wu_api_key, wu_reference_station_id


# To obtain reference values
wu = WUndergroundAPI(
    api_key=wu_api_key,
    default_station_id=wu_reference_station_id,
    units=units.METRIC_SI_UNITS,
)


def dashboard_page_fast():
    current_data_in = get_last_measurement_pack('weather_data', '0', '0')
    current_data_out = get_last_measurement_pack('weather_data', '0', '1')
    previous_data_in = get_last_measurement_pack('weather_data', '1', '0')
    previous_data_out = get_last_measurement_pack('weather_data', '1', '1')
    last_day_data_in = get_last_measurement_pack('weather_data', (float(60 * 24) / data_update_period) - 1, '0')
    last_day_data_out = get_last_measurement_pack('weather_data', (float(60 * 24) / data_update_period) - 1, '1')
    last_year_data_in = get_last_measurement_pack('weather_data', (float(60 * 24 * 365) / data_update_period) - 1, '0')
    last_year_data_out = get_last_measurement_pack('weather_data', (float(60 * 24 * 365) / data_update_period) - 1, '1')
    current_wind_data = get_last_measurement_pack('wind_data', '0')
    previous_wind_data = get_last_measurement_pack('weather_data', '1')
    last_day_wind_data = get_last_measurement_pack('weather_data', (float(60 * 24) / data_update_period) - 1)
    last_year_wind_data = get_last_measurement_pack('weather_data', (float(60 * 24 * 365) / data_update_period) - 1)
    wu_current = wu.current()

    return render_template("weather_station/weather_dashboard.html",
                           temperature_in=current_data_in['temperature'],
                           temperature_out=current_data_out['temperature'],
                           humidity_in=current_data_in['humidity'],
                           humidity_out=current_data_out['humidity'],
                           pressure=current_data_in['pressure'],
                           dew_point_in=current_data_in['dew_point'],
                           dew_point_out=current_data_out['dew_point'],
                           prev_temperature_in=previous_data_in['temperature'],
                           prev_temperature_out=previous_data_out['temperature'],
                           prev_humidity_in=previous_data_in['humidity'],
                           prev_humidity_out=previous_data_out['humidity'],
                           prev_pressure=previous_data_in['pressure'],
                           prev_dew_point_in=previous_data_in['dew_point'],
                           prev_dew_point_out=previous_data_out['dew_point'],
                           last_day_temperature_in=last_day_data_in['temperature'],
                           last_day_temperature_out=last_day_data_out['temperature'],
                           last_day_humidity_in=last_day_data_in['humidity'],
                           last_day_humidity_out=last_day_data_out['humidity'],
                           last_day_pressure=last_day_data_in['pressure'],
                           last_day_dew_point_in=last_day_data_in['dew_point'],
                           last_day_dew_point_out=last_day_data_out['dew_point'],
                           last_year_temperature_in=last_year_data_in['temperature'],
                           last_year_temperature_out=last_year_data_out['temperature'],
                           last_year_humidity_in=last_year_data_in['humidity'],
                           last_year_humidity_out=last_year_data_out['humidity'],
                           last_year_pressure=last_year_data_in['pressure'],
                           last_year_dew_point_in=last_year_data_in['dew_point'],
                           last_year_dew_point_out=last_year_data_out['dew_point'],
                           current_wind_speed=current_wind_data['avg_kmh'],
                           current_wind_gust=current_wind_data['max_kmh'],
                           prev_wind_speed=previous_wind_data['avg_kmh'],
                           prev_wind_gust=previous_wind_data['max_kmh'],
                           last_day_wind_speed=last_day_wind_data['avg_kmh'],
                           last_day_wind_gust=last_day_wind_data['max_kmh'],
                           last_year_wind_speed=last_year_wind_data['avg_kmh'],
                           last_year_wind_gust=last_year_wind_data['max_kmh'],
                           wind_heading=current_wind_data['heading'],
                           wind_heading_abbr=deg_to_heading(current_wind_data['heading']),
                           wu_temp=wu_current['observations'][0]['metric_si']['temp'],
                           wu_humidity=wu_current['observations'][0]['humidity'],
                           wu_pressure=int(int(wu_current['observations'][0]['metric_si']['pressure'])/1.33),
                           wu_dew_point=wu_current['observations'][0]['metric_si']['dewpt'],
                           wu_wind_speed=wu_current['observations'][0]['metric_si']['windSpeed'],
                           wu_wind_gust=wu_current['observations'][0]['metric_si']['windGust'],
                           wu_wind_direction=wu_current['observations'][0]['winddir'],
                           wu_wind_heading=deg_to_heading(int(wu_current['observations'][0]['winddir']))
                           )


def dashboard_page():
    # current data
    temperature_in = get_one_measurement('weather_data', 'temperature', '0', '0')
    temperature_out = get_one_measurement('weather_data', 'temperature', '0', '1')
    humidity_in = get_one_measurement('weather_data', 'humidity', '0', '0')
    humidity_out = get_one_measurement('weather_data', 'humidity', '0', '1')
    pressure = get_one_measurement('weather_data', 'pressure', '0', '0')
    dew_point_in = get_one_measurement('weather_data', 'dew_point', '0', '0')
    dew_point_out = get_one_measurement('weather_data', 'dew_point', '0', '1')
    wind_speed = get_one_measurement('wind_data', 'avg_speed', '0')
    wind_gust = get_one_measurement('wind_data', 'avg_gust', '0')
    # previous data
    prev_temperature_in = get_one_measurement('weather_data', 'temperature', '1', '0')
    prev_temperature_out = get_one_measurement('weather_data', 'temperature', '1', '1')
    prev_humidity_in = get_one_measurement('weather_data', 'humidity', '1', '0')
    prev_humidity_out = get_one_measurement('weather_data', 'humidity', '1', '1')
    prev_pressure = get_one_measurement('weather_data', 'pressure', '1', '0')
    prev_dew_point_in = get_one_measurement('dew_point', '1', '0')
    prev_dew_point_out = get_one_measurement('dew_point', '1', '1')
    prev_wind_speed = get_one_measurement('wind_data', 'avg_speed', '1')
    prev_wind_gust = get_one_measurement('wind_data', 'avg_gust', '1')
    # last day data
    period = (float(60 * 24) / data_update_period) - 1
    last_day_temperature_in = get_one_measurement('weather_data', 'temperature', period, '0')
    last_day_temperature_out = get_one_measurement('weather_data', 'temperature', period, '1')
    last_day_humidity_in = get_one_measurement('weather_data', 'humidity', period, '0')
    last_day_humidity_out = get_one_measurement('weather_data', 'humidity', period, '1')
    last_day_pressure = get_one_measurement('weather_data', 'pressure', period, '0')
    last_day_dew_point_in = get_one_measurement('weather_data', 'dew_point', period, '0')
    last_day_dew_point_out = get_one_measurement('weather_data', 'dew_point', period, '1')
    last_day_wind_speed = get_one_measurement('wind_data', 'avg_speed', period)
    last_day_wind_gust = get_one_measurement('wind_data', 'avg_gust', period)
    # last year data
    period = (float(60 * 24 * 365) / data_update_period) - 1
    last_year_temperature_in = get_one_measurement('weather_data', 'temperature', period, '0')
    last_year_temperature_out = get_one_measurement('weather_data', 'temperature', period, '1')
    last_year_humidity_in = get_one_measurement('weather_data', 'humidity', period, '0')
    last_year_humidity_out = get_one_measurement('weather_data', 'humidity', period, '1')
    last_year_pressure = get_one_measurement('weather_data', 'pressure', period, '0')
    last_year_dew_point_in = get_one_measurement('weather_data', 'dew_point', period, '0')
    last_year_dew_point_out = get_one_measurement('weather_data', 'dew_point', period, '1')
    last_year_wind_speed = get_one_measurement('wind_data', 'avg_speed', period)
    last_year_wind_gust = get_one_measurement('wind_data', 'avg_gust', period)
    # Wind heading
    wind_heading = get_one_measurement('wind_data', 'heading', '0')
    # WU forecast data
    wu_current = wu.current()
    wu_temp = wu_current['observations'][0]['metric_si']['temp']
    wu_humidity = wu_current['observations'][0]['humidity']
    wu_pressure = int(int(wu_current['observations'][0]['metric_si']['pressure'])/1.33)
    wu_dew_point = wu_current['observations'][0]['metric_si']['dewpt']
    wu_wind_speed = wu_current['observations'][0]['metric_si']['windSpeed']
    wu_wind_gust = wu_current['observations'][0]['metric_si']['windGust']
    wu_direction = wu_current['observations'][0]['winddir']
    wu_heading = deg_to_heading(int(wu_direction))

    return render_template("weather_station/weather_dashboard.html",
                           temperature_in=temperature_in,
                           temperature_out=temperature_out,
                           humidity_in=humidity_in,
                           humidity_out=humidity_out,
                           pressure=pressure,
                           dew_point_in=dew_point_in,
                           dew_point_out=dew_point_out,
                           prev_temperature_in=prev_temperature_in,
                           prev_temperature_out=prev_temperature_out,
                           prev_humidity_in=prev_humidity_in,
                           prev_humidity_out=prev_humidity_out,
                           prev_pressure=prev_pressure,
                           prev_dew_point_in=prev_dew_point_in,
                           prev_dew_point_out=prev_dew_point_out,
                           last_day_temperature_in=last_day_temperature_in,
                           last_day_temperature_out=last_day_temperature_out,
                           last_day_humidity_in=last_day_humidity_in,
                           last_day_humidity_out=last_day_humidity_out,
                           last_day_pressure=last_day_pressure,
                           last_day_dew_point_in=last_day_dew_point_in,
                           last_day_dew_point_out=last_day_dew_point_out,
                           last_year_temperature_in=last_year_temperature_in,
                           last_year_temperature_out=last_year_temperature_out,
                           last_year_humidity_in=last_year_humidity_in,
                           last_year_humidity_out=last_year_humidity_out,
                           last_year_pressure=last_year_pressure,
                           last_year_dew_point_in=last_year_dew_point_in,
                           last_year_dew_point_out=last_year_dew_point_out,
                           current_wind_speed=wind_speed,
                           current_wind_gust=wind_gust,
                           prev_wind_speed=prev_wind_speed,
                           prev_wind_gust=prev_wind_gust,
                           last_day_wind_speed=last_day_wind_speed,
                           last_day_wind_gust=last_day_wind_gust,
                           last_year_wind_speed=last_year_wind_speed,
                           last_year_wind_gust=last_year_wind_gust,
                           wind_heading=wind_heading,
                           wind_heading_abbr=deg_to_heading(wind_heading),
                           wu_temp=wu_temp,
                           wu_humidity=wu_humidity,
                           wu_pressure=wu_pressure,
                           wu_dew_point=wu_dew_point,
                           wu_wind_speed=wu_wind_speed,
                           wu_wind_gust=wu_wind_gust,
                           wu_wind_direction=wu_direction,
                           wu_wind_heading=wu_heading
                           )
