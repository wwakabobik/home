#!/bin/bash

# Notes:
# 1) place "home_server" folder content to /home/pi/web-server
# 2) place this script in at your home directory, ensure that it have execution permissions (chmod +x)
# 3) to run flask server on startup, add following line (without comment sign) to /etc/rc.local:
# /home/pi/flask_startup.sh &

sleep 10
cd /home/pi/web-server && sudo python3.7 app.py >>flask.log 2>&1
