from ftplib import FTP
from shutil import copyfile
from os import getcwd

import requests
from openweather_pws import Station
from narodmon import Narodmon

from db.queries import get_last_measurement_pack
from secure_data import wu_station_id, wu_station_pwd, wu_cam_id, wu_cam_pwd
from secure_data import pwsw_station_id, pwsw_api_key, ow_station_id, ow_api_key
from secure_data import narodmon_mac, narodmon_owner, narodmon_name, latitude, latitude, longitude, altitude
from pages.shared.tools import celsius_to_fahrenheit, fahrenheit_to_celsius, mmhg_to_baromin, heat_index, humidex
from pages.shared.tools import take_photo, baromin_to_mmhg


# Send data to services

def send_data():
    data = get_last_measurement_pack('0', '1')
    image = take_photo()
    wu_data = prepare_wu_format(data=data)
    response = str(send_data_to_wu(wu_data))
    response += str(send_data_to_pwsw(wu_data))
    response += str(send_data_to_ow(data))
    response += str(send_data_to_nardmon(data))
    send_image_to_wu(image)
    copyfile(image, f'{getcwd()}/camera/image.jpg')
    return response


def prepare_wu_format(data, timestamp=None):
    payload = f"&dateutc={timestamp}" if timestamp else "&dateutc=now"
    payload += "&action=updateraw"
    payload += "&humidity=" + "{0:.2f}".format(data['humidity'])
    payload += "&tempf=" + str(celsius_to_fahrenheit(data['temperature']))
    payload += "&baromin=" + str(mmhg_to_baromin(data['pressure']))
    payload += "&dewptf=" + str(celsius_to_fahrenheit(data['dew_point']))
    payload += "&heatindex=" + str(celsius_to_fahrenheit(heat_index(temp=data['temperature'], hum=data['humidity'])))
    payload += "&humidex=" + str(celsius_to_fahrenheit(humidex(t=data['temperature'], d=data['dew_point'])))
    payload += "&precip=" + str(data['precip'])
    payload += "&uv" + str(data['uv'])
    return payload


def send_data_to_wu(data):
    wu_url = "https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php?"
    wu_creds = "ID=" + wu_station_id + "&PASSWORD=" + wu_station_pwd
    response = requests.get(f'{wu_url}{wu_creds}{data}')
    return response.content


def send_image_to_wu(image):
    session = FTP('webcam.wunderground.com', wu_cam_id, wu_cam_pwd)
    file = open(image, 'rb')
    session.storbinary('image.jpg', file)
    file.close()
    session.quit()


def send_data_to_pwsw(data):
    pwsw_url = "http://www.pwsweather.com/pwsupdate/pwsupdate.php?"
    pwsw_creds = "ID=" + pwsw_station_id + "&PASSWORD=" + pwsw_api_key
    response = requests.get(f'{pwsw_url}{pwsw_creds}{data}')
    return response.content


def send_data_to_ow(data):
    pws = Station(api_key=ow_api_key, station_id=ow_station_id)
    response = pws.measurements.set(temperature=data['temperature'], humidity=data['humidity'],
                                    dew_point=data['dew_point'], pressure=data['pressure'],
                                    heat_index=fahrenheit_to_celsius(heat_index(temp=data['temperature'],
                                                                                hum=data['humidity'])),
                                    humidex=humidex(t=data['temperature'], d=data['dew_point']))
    return response


def send_data_to_nardmon(data):
    nm = Narodmon(mac=narodmon_mac, name=narodmon_name, owner=narodmon_owner,
                  lat=latitude, lon=longitude, alt=altitude)
    temperature = nm.via_json.prepare_sensor_data(id_in="TEMPC", value=data['temperature'])
    pressure = nm.via_json.prepare_sensor_data(id_in="MMHG", value=(data['pressure']))
    humidity = nm.via_json.prepare_sensor_data(id_in="HUM", value=data['humidity'])
    dew_point = nm.via_json.prepare_sensor_data(id_in="DEW", value=data['dew_point'])
    sensors = [temperature, pressure, humidity, dew_point]
    response = nm.via_json.send_short_data(sensors=sensors)
    return response


def send_data_to_informer():
    data_in = get_last_measurement_pack('weather_data', '0', '0')
    data_out = get_last_measurement_pack('weather_data', '0', '1')
    pressure = int((data_in['pressure']+data_out['pressure'])/2)
    formatted_string = f"IN: T={data_in['temperature']}*C, " \
                       f"H={data_in['humidity']}% | " \
                       f"OUT: T={data_out['temperature']}*C, " \
                       f"H={data_out['humidity']}%, " \
                       f"DP={data_out['dew_point']}*C | " \
                       f"P={pressure} mmhg"
    return formatted_string
