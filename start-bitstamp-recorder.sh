#!/bin/bash
# This script starts bitstamp-recorder.py 

cd ~/bitstamp-recorder
python bitstamp-recorder.py &
echo 'bitstamp-recorder.py has been started' | ssmtp root & 2> /dev/null

