# websocket\_recorder

## What is it?

A Python module exposing class WebsocketRecorder allowing you to record incoming WebSocket messages into text files. Each received WebSocket message is written on a single line. On top of the original WebSocket message, some meta info is written too in the same line (e.g. timestamp, hostname). 

## What is a WebSocket?
WebSocket is a communications protocol providing full-duplex communications channels over a single TCP connection. In a full-duplex connection you are able to send and receive message simultaneously. Whereas in hald-duplex you send and receive message sequentially, not simultaneously. The WebSockets protocol has been standardized in RFC 6455.


## Why do I need it?
You need it to record the data to analyze later, for example news articles send through WebSockets or to record data from bitcoin exchanges, like Bitstamp.

## Dependencies
[ws4py](https://ws4py.readthedocs.org/en/latest/), version 0.3.3. at least. 

## Installation on Linux
```
cd ~
git clone git@github.com:Dmitrii-I/websocket_recorder.git

# create a Python package directory where we will put this module in
mkdir -p ~/.local/lib/python2.7/site-packages 

# check that this directory is picked up by Python
python -c "import sys; sys.path"
# and if not check that you are using correct Python version. Try out these as well:
/usr/bin/env python -c "import sys; sys.path"

# create a symlink to the module:
ln -s ~/websocket_recorder ~/.local/lib/python2.7/site-packages/websocket_recorder

# create logging directory
sudo mkdir -p /var/log/websocket_recorder
# make sure the directory is writeable by the user who will run websocket_recorder

# Test it:
python -c "import websocket_recorder"
```
## Usage: 
```
import websocket_recorder
wsrec = WebsocketRecorder(...)
wsrec.connect()
wsrec.run_forever()
```

## Details
I have considered compressing the data file after it has reached max_lines, but that would take about 0.5 second for a 1000 line file.
I do not want to introduce this latency into the recorder. Compressing therefore needs to be done outside this websocket_recorder.py.
