# websocket\_recorder

## What is it?

A Python script to record incoming WebSocket messages into text files. Each received WebSocket message is logged on one line into a text file. On top of the original WebSocket message, some meta info is written too in the same line (e.g. timestamp, hostname). The script can be used with any WebSocket source. For each source create a config file similar to config examples provided in the directory settings.

## Dependencies
[ws4py](https://ws4py.readthedocs.org/en/latest/), version 0.3.3. at least. 

## Installation on Linux
```
cd ~
git clone https://github.com/Dmitrii-I/websocket-recorder.git
```
## Usage: 
```
python websocket-recorder.py settings/some-websocket-source.conf &
```
The ampersand makes sure the script in background as a child of your terminal process. If you quit your terminal, the script stops to. To run it forever even if you quit, daemonize it, or use https://github.com/Dmitrii-I/bash-scripts/blob/master/keep-running.sh

