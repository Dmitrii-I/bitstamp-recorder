#!/bin/bash

# This script restarts websocket_recorder.py. Strictly speaking, it is not a restart. We first 
# get the PID of current running instance of websocket_recorder.py, then start a new
# instance. For couple seconds we have two instances recording same data to two 
# different text files. After couple second pass, we stop the old instance.
# This overlap ensures we not miss ticks. Also note that you cannot have two instances
# write to same file because in some cases both instances will write to same line
# in the text file and you end up with mumbo-jumbo.

(
LOG="recorder.log"
# get the PID of current instance
pid_old_instance=$(ps -ef | grep "websocket_recorder.py" | grep -v grep | tr -s " " | cut -d " " -f2)

./start-recorder.sh
timestamp=$(date +"%Y-%m-%d %H:%M:%S.%N")
echo -ne "$timestamp\t" >> $LOG
echo -ne "restart-recorder.sh\tNew recorder instance has been started\n" >> $LOG

timestamp=$(date +"%Y-%m-%d %H:%M:%S.%N")
echo -ne "$timestamp\t" >> $LOG
echo -ne "restart-recorder.sh\tWaiting 1 minute before stopping old instance to not miss data if new instance is not recording immediately\n" >> $LOG
sleep 60

kill $pid_old_instance
timestamp=$(date +"%Y-%m-%d %H:%M:%S.%N")
echo -ne "$timestamp\t" >> $LOG
echo -ne "restart-recorder.sh\tDone waiting. Will now stop old instance (SIGTERM) with PID $pid_old_instance\n" >> $LOG
) & # let the script run in the background. We do not want to wait one minute in the terminal
