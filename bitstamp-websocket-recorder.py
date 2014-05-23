#!/usr/bin/env python 
# This Python module records the data from the websocket stream of Bitstamp (a bitcoin exchange).
# Bitstamp does not stream the data from their own servers, but use pusher.com as a hosted API
# provider. 
#
# This Bitstamp websocket stream formats all outgoing messages in JSON. Incoming messages (the ones you send to the 
# websocket) should also be JSON formatted. 
#
# Each received websocket message is logged on one line in a csv file. On top of the original message,
# on the same line in the log, we also record the timestamp of receiving message. 
#
# This Python module depends on ws4py, version 0.3.3. at least. 


from ws4py.client.threadedclient import WebSocketClient # trim the fat, import only one class
import datetime
import subprocess
import sys

sys.stdout = open("recorder.log", "a")
sys.stderr = open("recorder.log", "a")

class BitstampWebsocketRecorder(WebSocketClient):
        """ This class inherits from WebSocketClient class. We extend the __init__ method a bit. """
        
        def __init__(self, url):
		# url is the websocket url, excluding the channel string
                super(BitstampWebsocketRecorder, self).__init__(url)
                self.logfile = open(self.new_log_filename(), "a")
                self.logfile_lines_counter = 0
                # one line is about 1 KB. If log reaches max_lines start to writing new logfile:
		self.max_lines = 10000 

        def new_log_filename(self):
                return(datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mh%Ss_bitstamp_data.csv"))

        def opened(self):
                # Subscribe to the only two Bitstamp websocket channels: live_trades and order_book
                self.send('{"data": {"channel": "live_trades"}, "event": "pusher:subscribe"}')
                self.send('{"data": {"channel": "order_book"}, "event": "pusher:subscribe"}')
                 
        def closed(self, code, reason=None):
                # This method is called if the websocket connection is closed (by server or connection error)
		# Start a new Bitstamp recorder instance. We do not want to miss any data.
		# Send an email to root user of the Linux server we are running on (alias set in /etc/ssmtp/ssmtp.conf) 
		subprocess.call("echo 'Bitstamp recorder stopped nondeliberately. Will attempt to start it right away.' | ssmtp root &", shell=True)
		subprocess.call("./start-recorder.sh", shell=True)
                exit_message = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f UTC, ") + "Recorder stopped. Code: " + \
                        str(code) + ". Reason: " + str(reason) + "\n"
		self.logfile.write(exit_message)
		print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f UTC, "), "Recorder stopped. Code: ", code, ". Reason: ", reason, "\n")
                self.logfile.close()

        def received_message(self, m):
                self.logfile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f UTC, ") + str(m) + "\n")                
                self.logfile_lines_counter += 1
                if self.logfile_lines_counter >= self.max_lines:
                        self.logfile.close() # close the full logfile
                        self.logfile = open(self.new_log_filename(), 'a') # and open a new one
                        self.logfile_lines_counter = 0

if __name__ == '__main__':
        # Bitstamp uses hosted websocket service from pusher.com. Bitstamp's app key is de504dc5763aeef9ff52
        recorder = BitstampWebsocketRecorder('ws://ws.pusherapp.com:80/app/de504dc5763aeef9ff52?client=justme&version=0.2.0&protocol=6')
        recorder.connect()
        recorder.run_forever()
