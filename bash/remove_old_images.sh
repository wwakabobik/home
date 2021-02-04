#!/bin/bash bash

# Notes:
# This file will remove all files in camera folder older than 7 days, just run in via cron periodically (i.e. daily).
find /home/pi/web-server/camera/ -type f -mtime +7 -name '*.jpg' -execdir rm -- '{}' \;