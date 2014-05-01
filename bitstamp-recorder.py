#!/usr/bin/env python 
# use ws4py version 0.3.3 at least. Version 0.2.4 will not work with this script.
from ws4py.client.threadedclient import WebSocketClient # trim the fat, import only one class
import datetime
import sys
import subprocess


class websocket_client(WebSocketClient): # DummyClient inherits from WebSocketClient
        def opened(self):
                print("opened")
                ws.send('{"data": {"channel": "live_trades"}, "event": "pusher:subscribe"}')
                ws.send('{"data": {"channel": "order_book"}, "event": "pusher:subscribe"}')
                 
        def closed(self, code, reason=None):
                print("closed")

        def received_message(self, m):
                print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f UTC, ") + str(m) + "\n")                

if __name__ == '__main__': # true if this script is run directly
    try:
        ws = websocket_client('ws://ws.pusherapp.com:80/app/de504dc5763aeef9ff52?client=justme&version=0.2.0&protocol=6')
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()

