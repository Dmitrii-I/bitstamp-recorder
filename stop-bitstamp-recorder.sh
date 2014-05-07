#!/bin/bash

# get the PID of current instance
pid_recorder=$(ps -ef | grep "python.*bitstamp-recorder.py" | grep -v grep | tr -s " " | cut -d " " -f2)
echo "Will now stop bitstamp-recorder.py with PID $pid_recorder"
kill -s 9 $pid_recorder
echo 'bitstamp-recorder.py stopped deliberately through stop-bitstamp-recorder.sh. Will not run unless started manually with start-bistamp-recorder.sh' | ssmtp root &

# pid_monitor=$(ps -ef | grep "monitor-bitstamp-recorder.sh" | grep -v grep | tr -s " " | cut -d " " -f2)
# kill -s 9 $pid_monitor
