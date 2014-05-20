#!/bin/bash

# This script keeps checking every 60 seconds whether the bitstamp recorder is running
# If it is not running, send an email to root and quit
# To daemonize this script we put braces around it and end with ampersand &
# Learned this trick here: http://stackoverflow.com/questions/3430330/best-way-to-make-a-shell-script-daemon

(
while ~/bitstamp-recorder/is-recorder-running.sh; do
	timestamp=$(date +"%Y-%m-%d %H:%M:%S.%N")
	echo -n "$timestamp " >> ~/bitstamp-recorder/recorder.log
	echo "Bitstamp websocket recorder is still running" >> ~/bitstamp-recorder/recorder.log
	sleep 60
done

# if bitstamp-recorder.py is not running, send mail to root user (alias set in /etc/ssmtp/ssmtp.conf) and quit
echo "Message from monitor-recorder.sh: Recorder is not running anymore for some reason. Please check and start manually." | ssmtp root &
) &