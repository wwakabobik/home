#!/bin/bash

# Notes:
# This file is health check for running server process, just run in via cron periodically (i.e. 5 min).

if  ps -aux | grep '[/]bin/bash /home/pi/flask_startup.sh' > /dev/null
then
    :
else
    /bin/bash /home/pi/flask_startup.sh
fi
