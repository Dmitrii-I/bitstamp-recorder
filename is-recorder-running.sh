#!/bin/bash

# This script retruns exit code 0 (true) if Bitstamp recorder is running on the system
ps -ef | grep "python bitstamp-websocket-recorder.py" | grep -v grep > /dev/null

