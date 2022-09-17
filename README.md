## Home Online Monitoring Environment

This repo contains project of smart home.

[![H.O.M.E.](https://img.youtube.com/vi/eQUUWfOznbs/0.jpg)](https://www.youtube.com/watch?v=eQUUWfOznbs)
Detail article you can find on [Habr](https://habr.com/ru/post/543146/). 

Home server based on Raspberry Pi (originally rev 1.0 B+).
All other devices are IOT devices like ESP8266 or Arduino+LoRa.

![HOME. concept](https://github.com/wwakabobik/home/blob/master/screenshots/home_concept.jpeg)

Main goal is to collect, store and process data, such as:
- real-time remote weather monitoring and reporting
- real-time remote monitoring of wind data
- real-time remote monitoring of windmill controller
- management of home appliances (i.e. dynamic light, boilers via ZONT-ONLINE) [TBD]

Data may be sent to some external display, if needed, by requesting via API.

Web server weather status dashboard (web):

![HOME dashboard](https://github.com/wwakabobik/home/blob/master/screenshots/home_dashboard.png)

As well as detailed monitored parameter details:

![HOME dashboard](https://github.com/wwakabobik/home/blob/master/screenshots/home_chart.png)

If you have a RPiCam, you can also get, store and share photos and videos from it:

![HOME camera](https://github.com/wwakabobik/home/blob/master/screenshots/home_camera.png)

Weather params may be shared to:
- [WeatherUnderground](https://www.wunderground.com/)
- [PWSWeather](https://www.pwsweather.com/)
- [OpenWeatherMap](https://openweathermap.org/) via my API, see detailed in repo: [openweather_pws](https://github.com/wwakabobik/openweather_pws) / [pypi](https://pypi.org/project/openweather-pws/)
- [NarodMon](https://narodmon.ru/) via my API, see detailed in repo: [narodmon](https://github.com/wwakabobik/narodmon) / [pypi](https://pypi.org/project/narodmon-python-api/)

Project uses flask as web-server, plotly as chart engine and other IOT-related packages.


