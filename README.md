# websocket\_recorder

## What is it?

A Python script to record incoming WebSocket messages into text files. Each received WebSocket message is logged on one line into a text file. On top of the original WebSocket message, some meta info is written too in the same line (e.g. timestamp, hostname). The script can be used with any WebSocket source. For each source create a config file similar to config examples provided in the directory settings.

## Why do I need it?
You need it to record the data to analyze later. For example you record news articles coming out of a news stream, where each news article is sent to you as one WebSocket message. Some bitcoin exchanges, like Bitstamp, provide streaming prices through WebSockets.

## Dependencies
[ws4py](https://ws4py.readthedocs.org/en/latest/), version 0.3.3. at least. 

## Installation on Linux
```
cd ~
git clone https://github.com/Dmitrii-I/websocket_recorder.git
```
## Usage: 
```
python websocket-recorder.py settings/some-websocket-source.conf &
```
The ampersand at the end runs the script in the background as a child process of your terminal process. If you quit your terminal, the script will quit too. To run it forever, even if you quit the terminal use https://github.com/Dmitrii-I/bash-scripts/blob/master/keep-running.sh or daemonize it somehow.

