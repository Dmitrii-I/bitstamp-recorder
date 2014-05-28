#!/bin/bash

LOG="recorder.log"
# get the PID of current instance
pid_recorder=$(ps -ef | grep "websocket_recorder.py" | grep -v grep | tr -s " " | cut -d " " -f2)
kill $pid_recorder
timestamp=$(date +"%Y-%m-%d %H:%M:%S.%N")
echo -ne "$timestamp\t" >> $LOG
echo -ne "stop-recorder.sh\tRecorder with PID $pid_recorder has been stopped\n" >> $LOG
