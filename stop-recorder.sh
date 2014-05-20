#!/bin/bash

# get the PID of current instance
pid_recorder=$(ps -ef | grep "python.*bitstamp-websocket-recorder.py" | grep -v grep | tr -s " " | cut -d " " -f2)
echo "Will now stop the recorder with PID $pid_recorder"
kill -s 9 $pid_recorder
echo 'Bitstamp recorder stopped deliberately through stop-recorder.sh. Recorder will not be started, unless started manually with start-recorder.sh' | ssmtp root &
