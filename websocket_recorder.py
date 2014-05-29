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
        def __init__(self, url, msg_to_send, max_lines, script_filename, machine_id, ws_name):
                self.url = url
                self.msg_to_send = msg_to_send
		self.max_lines = max_lines 
                self.recorder_version = self.md5sum(script_filename)
                self.machine_id = machine_id
                self.ws_name = ws_name
                self.recorder_session_id = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f UTC")
                self.datafile = open(self.new_csv_file(), "a")
                self.datafile_lines_counter = 0
                super(WebsocketRecorder, self).__init__(self.url)
                
        def new_csv_file(self):
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
                filename = timestamp + self.ws_name + self.machine_id + ".csv"
                return(filename)

        def opened(self):
                # Send initial messages to the websocket
                for message in self.msg_to_send:
                        self.send(message)
                 
        def closed(self, code, reason=None):
                # This method is called if the websocket connection is closed (by server or connection error)
                exit_message = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f UTC, ") + "Recorder stopped. Code: " + \
                        str(code) + ". Reason: " + str(reason) + "\n"
		print(exit_message)
                self.datafile.write(exit_message)
                self.datafile.close()

        def received_message(self, ws_msg):
                message = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f UTC, ") + str(ws_msg) + ", " + self.recorder_version +\
                                ", " + self.machine_id + ", " + self.recorder_session_id + ", " + self.url + "\n"
                self.datafile.write(message)                
                self.datafile_lines_counter += 1
                # one line is about 1 KB. If log reaches max_lines write to new datafile:
                if self.datafile_lines_counter >= self.max_lines:
                        self.datafile.close() # close the full datafile
                        self.datafile = open(self.new_csv_file(), 'a') # and open a new one
                        self.datafile_lines_counter = 0

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
        recorder = WebsocketRecorder(url, msg_to_send, max_lines, script_filename, machine_id, ws_name)
        recorder.connect()
        recorder.run_forever()
