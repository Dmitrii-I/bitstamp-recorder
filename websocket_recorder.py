#!/usr/bin/env python 
# This Python module records incoming message for a websocket stream.
# Each received websocket message is logged on one line in a csv file. On top of the original message,
# on the same line in the log, we also record the timestamp and some other metadata. 
#
# This Python module depends on ws4py, version 0.3.3. at least. 

from ws4py.client.threadedclient import WebSocketClient # trim the fat, import only one class
import datetime
import subprocess
import sys
import hashlib

class WebsocketRecorder(WebSocketClient):
        """ This class inherits from WebSocketClient class. We extend the __init__ method a bit. """
        def __init__(self, url, msg_to_send, max_lines, script_filename, machine_id):
                self.url = url
                self.msg_to_send = msg_to_send
		self.max_lines = max_lines 
                self.recorder_version = self.md5sum(script_filename)
                self.machine_id = machine_id
                self.recorder_session_id = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f UTC")
                self.logfile = open(self.new_csv_file(), "a")
                self.logfile_lines_counter = 0
                super(WebsocketRecorder, self).__init__(self.url)
                
        def new_csv_file(self):
                return(datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mh%Ss_websocket_data.csv"))

        def opened(self):
                # Send initial messages to the websocket
                for message in self.msg_to_send:
                        self.send(message)
                 
        def closed(self, code, reason=None):
                # This method is called if the websocket connection is closed (by server or connection error)
		# Start a new Bitstamp recorder instance. We do not want to miss any data.
		# Send an email to root user of the Linux server we are running on (alias set in /etc/ssmtp/ssmtp.conf) 
                exit_message = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f UTC, ") + "Recorder stopped. Code: " + \
                        str(code) + ". Reason: " + str(reason) + "\n"
		self.logfile.write(exit_message)
                self.logfile.close()

        def received_message(self, ws_msg):
                message = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f UTC, ") + str(ws_msg) + ", " + self.recorder_version +\
                                ", " + self.machine_id + ", " + self.recorder_session_id + "\n"
                self.logfile.write(message)                
                self.logfile_lines_counter += 1
                # one line is about 1 KB. If log reaches max_lines write to new logfile:
                if self.logfile_lines_counter >= self.max_lines:
                        self.logfile.close() # close the full logfile
                        self.logfile = open(self.new_csv_file(), 'a') # and open a new one
                        self.logfile_lines_counter = 0

        def md5sum(self, filename):
                hasher = hashlib.md5()
                with open(filename, 'rb') as afile:
                        buf = afile.read()
                        hasher.update(buf)
                return(hasher.hexdigest())
 

if __name__ == '__main__':
        script_filename = sys.argv[0]
        settings_file = sys.argv[1]
        execfile(settings_file) # load the settings specific to a particular websocket
        sys.stdout = open(stdout_file, "a")
        sys.stderr = open(stderr_file, "a")
        recorder = WebsocketRecorder(url, msg_to_send, max_lines, script_filename, machine_id)
        recorder.connect()
        recorder.run_forever()
