#!/bin/bash

# This script retruns exit code 0 (true) if there is bitstamp-recorder.py running on the system
ps -ef | grep "python.*bitstamp-recorder.py" | grep -v grep > /dev/null

