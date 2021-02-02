from flask import render_template
from wunderground_pws import WUndergroundAPI, units

from db.weather_station import get_one_measurement, data_update_period, get_last_measurement_pack
from secure_data import wu_api_key, wu_reference_station_id


wu = WUndergroundAPI(
    api_key=wu_api_key,
    default_station_id=wu_reference_station_id,
    units=units.METRIC_SI_UNITS,
)


def deg_to_heading(degrees=0):
    dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    ix = round(degrees / (360. / len(dirs)))
    return dirs[ix % len(dirs)]


def dashboard_page_fast():
    current_data_in = get_last_measurement_pack('0', '0')
    current_data_out = get_last_measurement_pack('0', '1')
    previous_data_in = get_last_measurement_pack('0', '0')
    previous_data_out = get_last_measurement_pack('0', '1')
    last_day_data_in = get_last_measurement_pack((float(60 * 24) / data_update_period) - 1, '0')
    last_day_data_out = get_last_measurement_pack((float(60 * 24) / data_update_period) - 1, '1')
    last_year_data_in = get_last_measurement_pack((float(60 * 24 * 365) / data_update_period) - 1, '0')
    last_year_data_out = get_last_measurement_pack((float(60 * 24 * 365) / data_update_period) - 1, '1')

    return render_template("weather_station/dashboard.html",
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
                           wu_temp=wu.current()['observations'][0]['metric_si']['temp'],
                           wu_humidity=wu.current()['observations'][0]['humidity'],
                           wu_pressure=int(int(wu.current()['observations'][0]['metric_si']['pressure'])/1.33),
                           wu_dew_point=wu.current()['observations'][0]['metric_si']['dewpt'],
                           wu_wind_speed=wu.current()['observations'][0]['metric_si']['windSpeed'],
                           wu_wind_gust=wu.current()['observations'][0]['metric_si']['windGust'],
                           wu_wind_direction=wu.current()['observations'][0]['winddir'],
                           wu_wind_heading=deg_to_heading(int(wu.current()['observations'][0]['winddir']))
                           )


def dashboard_page():
    # current data
    temperature_in = get_one_measurement('temperature', '0', '0')
    temperature_out = get_one_measurement('temperature', '0', '1')
    humidity_in = get_one_measurement('humidity', '0', '0')
    humidity_out = get_one_measurement('humidity', '0', '1')
    pressure = get_one_measurement('pressure', '0', '0')
    dew_point_in = get_one_measurement('dew_point', '0', '0')
    dew_point_out = get_one_measurement('dew_point', '0', '1')
    # previous data
    prev_temperature_in = get_one_measurement('temperature', '1', '0')
    prev_temperature_out = get_one_measurement('temperature', '1', '1')
    prev_humidity_in = get_one_measurement('humidity', '1', '0')
    prev_humidity_out = get_one_measurement('humidity', '1', '1')
    prev_pressure = get_one_measurement('pressure', '1', '0')
    prev_dew_point_in = get_one_measurement('dew_point', '1', '0')
    prev_dew_point_out = get_one_measurement('dew_point', '1', '1')
    # last day data
    period = (float(60 * 24) / data_update_period) - 1
    last_day_temperature_in = get_one_measurement('temperature', period, '0')
    last_day_temperature_out = get_one_measurement('temperature', period, '1')
    last_day_humidity_in = get_one_measurement('humidity', period, '0')
    last_day_humidity_out = get_one_measurement('humidity', period, '1')
    last_day_pressure = get_one_measurement('pressure', period, '0')
    last_day_dew_point_in = get_one_measurement('dew_point', period, '0')
    last_day_dew_point_out = get_one_measurement('dew_point', period, '1')
    # last year data
    period = (float(60 * 24 * 365) / data_update_period) - 1
    last_year_temperature_in = get_one_measurement('temperature', period, '0')
    last_year_temperature_out = get_one_measurement('temperature', period, '1')
    last_year_humidity_in = get_one_measurement('humidity', period, '0')
    last_year_humidity_out = get_one_measurement('humidity', period, '1')
    last_year_pressure = get_one_measurement('pressure', period, '0')
    last_year_dew_point_in = get_one_measurement('dew_point', period, '0')
    last_year_dew_point_out = get_one_measurement('dew_point', period, '1')
    # WU forecast data
    wu_temp = wu.current()['observations'][0]['metric_si']['temp']
    wu_humidity = wu.current()['observations'][0]['humidity']
    wu_pressure = int(int(wu.current()['observations'][0]['metric_si']['pressure'])/1.33)
    wu_dew_point = wu.current()['observations'][0]['metric_si']['dewpt']
    wu_wind_speed = wu.current()['observations'][0]['metric_si']['windSpeed']
    wu_wind_gust = wu.current()['observations'][0]['metric_si']['windGust']
    wu_direction = wu.current()['observations'][0]['winddir']
    wu_heading = deg_to_heading(int(wu_direction))

    return render_template("weather_station/dashboard.html",
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
                           wu_temp=wu_temp,
                           wu_humidity=wu_humidity,
                           wu_pressure=wu_pressure,
                           wu_dew_point=wu_dew_point,
                           wu_wind_speed=wu_wind_speed,
                           wu_wind_gust=wu_wind_gust,
                           wu_wind_direction=wu_direction,
                           wu_wind_heading=wu_heading
                           )
