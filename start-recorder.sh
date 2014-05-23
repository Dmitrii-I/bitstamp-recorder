#!/bin/bash
# This script starts bitstamp-websocket-recorder.py. It is better to start the recorder through the script because 
# then the recorder will have parent PID of 1. If you run:
# python bitstamp-websocket-recorder.py &
# from the terminal, then the python process will get the parent PID of your terminal.
# When you exit the terminal, the python process will be stopped. This is not the behavior we want.

./bitstamp-websocket-recorder.py &
timestamp=$(date +"%Y-%m-%d %H:%M:%S.%N")
echo -ne "$timestamp\t" >> recorder.log
echo -ne "start-recorder.sh\tBitstamp recorder has been started\n" >> recorder.log
