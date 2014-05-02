#!/usr/bin/env python 
# use ws4py version 0.3.3 at least. Version 0.2.4 will not work with this script.

from ws4py.client.threadedclient import WebSocketClient # trim the fat, import only one class
import datetime
import sys
import subprocess
import logging
import logging.handlers


class BitstampRecorder(WebSocketClient):
        """ This class records websocket data from the Bitstamp bitcoin exchange.
        It inherits from WebSocketClient, and add couple things to the __init__ method."""
        
        def __init__(self, url):
                super(BitstampRecorder, self).__init__(url)
                self.logfile = open(self.new_log_filename(), "a")
                self.logfile_lines_counter = 0
                self.max_lines = 10000 # one line is about 1 KB. If logfile reaches max_lines, we start to write in new file

        def new_log_filename(self):
                return(datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mh%Ss_bitstamp_data.csv"))

        def opened(self):
                # Bitstamp has two websocket channels: live_trades and order_book
                self.send('{"data": {"channel": "live_trades"}, "event": "pusher:subscribe"}')
                self.send('{"data": {"channel": "order_book"}, "event": "pusher:subscribe"}')
                 
        def closed(self, code, reason=None):
                print("closed")

        def received_message(self, m):
                self.logfile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f UTC, ") + str(m) + "\n")                
                self.logfile_lines_counter += 1
                if self.logfile_lines_counter >= self.max_lines:
                        self.logfile.close() # close the full logfile
                        self.logfile = open(self.new_log_filename(), 'a') # and open a new one
                        self.logfile_lines_counter = 0

if __name__ == '__main__':
        try:
                # Bitstamp uses hosted websocket service from pusher.com. Bitstamp's app key is de504dc5763aeef9ff52
                recorder = BitstampRecorder('ws://ws.pusherapp.com:80/app/de504dc5763aeef9ff52?client=justme&version=0.2.0&protocol=6')
                recorder.connect()
                recorder.run_forever()

        except KeyboardInterrupt:
                recorder.logfile.close()
                print("closed")
                recorder.close()

