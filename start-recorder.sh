#!/bin/bash
# This script starts bitstamp-websocket-recorder.py. It is better to start the recorder through the script because 
# then the recorder will have parent PID of 1. If you run:
# python bitstamp-websocket-recorder.py &
# from the terminal, then the python process will get the parent PID of your terminal.
# When you exit the terminal, the python process will be stopped. This is not the behavior we want.

python bitstamp-websocket-recorder.py &
echo 'Bitstamp recorder has been started' | ssmtp root & 2> /dev/null
