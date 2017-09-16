# websocket\_recorder

A Python module to record incoming WebSocket messages into text files. Each received WebSocket message plus meta data (hostname, timestamp) is written on a single line as JSON.

## Dependencies
[ws4py](https://ws4py.readthedocs.org/en/latest/), version 0.3.3. at least. 

## Installation on Linux

```
git clone git@github.com:Dmitrii-I/websocket_recorder.git
cd websocket_recorder
pip install ./ --user --upgrade


# create logging directory
sudo mkdir -p /var/log/websocket_recorder
# make sure the directory is writeable by the user who will run websocket_recorder
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
