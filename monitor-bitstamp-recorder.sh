#!/bin/bash

# This script keeps checking every 60 seconds whether the bitstamp recorder is running
# If it is not running, send an email to root and quit

while ~/bitstamp-recorder/is-bitstamp-recorder-running.sh; do
	sleep 60
done

# if bitstamp-recorder.py is not running, send mail to root user (alias set in /etc/ssmtp/ssmtp.conf) and quit
echo "Message from monitor-bistamp-recorder.sh: bistamp-recorder.py not running anymore for some reason. Please check and start manually." | ssmtp root &
