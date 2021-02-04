from ftplib import FTP

import requests
from openweather_pws import Station

from db.queries import get_last_measurement_pack
from secure_data import wu_station_id, wu_station_pwd, wu_cam_id, wu_cam_pwd
from secure_data import pwsw_station_id, pwsw_api_key, ow_station_id, ow_api_key
from pages.shared.tools import celsius_to_fahrenheit, fahrenheit_to_celsius, mmhg_to_baromin, heat_index, humidex
from pages.shared.tools import take_photo


# Send data to services

def send_data():
    data = get_last_measurement_pack('0', '1')
    image = take_photo()
    wu_data = prepare_wu_format(data=data)
    response = str(send_data_to_wu(wu_data))
    response += str(send_data_to_pwsw(wu_data))
    response += str(send_data_to_ow(data))
    send_image_to_wu(image)
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
    wu_url = "http://www.pwsweather.com/pwsupdate/pwsupdate.php?"
    wu_creds = "ID=" + pwsw_station_id + "&PASSWORD=" + pwsw_api_key
    response = requests.get(f'{wu_url}{wu_creds}{data}')
    return response.content


def send_data_to_ow(data):
    pws = Station(api_key=ow_api_key, station_id=ow_station_id)
    response = pws.measurements.set(temperature=data['temperature'], humidity=data['humidity'],
                                    dew_point=data['dew_point'], pressure=data['pressure'],
                                    heat_index=fahrenheit_to_celsius(heat_index(temp=data['temperature'],
                                                                                hum=data['humidity'])),
                                    humidex=humidex(t=data['temperature'], d=data['dew_point']))
    return response
