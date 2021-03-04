#!/bin/bash

PATH_TO_PHOTO=`/usr/bin/wget -O - -q -t 1 http://0.0.0.0/api/v1/capture_photo`
REQUEST='curl -F YOUR_NARODMON_API_KEY=@'$PATH_TO_PHOTO' http://narodmon.ru/post'
RESULT=`$REQUEST` >/dev/null 2>&1
