#!/bin/bash

# This script starts websocket_recorder.py as a daemon. Starting it through 
# bash script is preferred because it gives the recorder parent PID 1. 
# If you just run 'python websocket_recorder.py &' in terminal (ampersand
# at the end forces the command to run in background), the Python process 
# will get the parent PID of your terminal. When you exit the terminal, 
# the recorder will be stopped. This may not be the behavior you want and 
# so this script can be used.
#
# More robust approach would be to daemonize the whole websocket_recorder.py
# in Python itself rather then relying on a  bash script. To do that, look here
# for tips:
# http://code.activestate.com/recipes/66012-fork-a-daemon-process-on-unix/
# http://blog.scphillips.com/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/
# http://stackoverflow.com/questions/473620/how-do-you-create-a-daemon-in-python

config_file=$1
logfile="recorder.log"
./websocket_recorder.py $config_file &

timestamp=$(date +"%Y-%m-%d %H:%M:%S.%N")
echo -ne "$timestamp\t" >> $logfile
echo -ne "start-recorder.sh\twebsocket_recorder.py has been started\n" >> $logfile
