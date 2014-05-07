#!/bin/bash

# This script restarts bitstamp-recorder.py. Strictly speaking, it is not a restart. We first 
# get the PID of current running instance of bitstamp-recorder.py, then start a new
# instance. For couple seconds we have two instances recording same data to two 
# different text files. After couple second pass, we stop the old instance.
# This overlap ensures we not miss ticks. Also note that you cannot have two instances
# write to same file because in some cases both instances will write to same line
# in the text file and you end up with mumbo-jumbo.

# get the PID of current instance
pid_old_instance=$(ps -ef | grep "python bitstamp-recorder.py" | grep -v grep | tr -s " " | cut -d " " -f2)
echo "PID old instance is $pid_old_instance"

# Start new instance
~/bitstamp-recorder/start-bitstamp-recorder.sh

echo "Will now wait one minute before stopping old instance with PID $pid_old_instance in order not to miss data if new instance is not recording immediately."
sleep 60
echo "Done waiting. Will now stop old instance with PID $pid_old_instance"
kill $pid_old_instance
echo "Done stopping old instance. Completed all steps. This script will quit now"
echo 'bitstamp-recorder.py stopped deliberately through stop-bitstamp-recorder.sh as a planned restart. New instance of bitstamp-recorder.py is already running.' | ssmtp root &
