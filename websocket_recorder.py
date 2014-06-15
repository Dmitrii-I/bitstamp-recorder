#!/usr/bin/env python 
#
# This Python module records incoming message for a websocket stream. 
# Each received websocket message is logged on one line in a csv file. On top of the original message,
# on the same line in the log, we also record the timestamp and some other metadata. 
#
# Tested only on Linux.
#
# Dependencies: ws4py, version 0.3.3. at least. 
#
# Usage: python websocket-recorder.py settings/some-websocket-source.conf &
# The ampersand makes sure the script in background as a child of your terminal process.
# If you quit your terminal, the script stops to. To run it forever even if you quit,
# daemonize it, or use https://github.com/Dmitrii-I/bash-scripts/blob/master/keep-running.sh

from ws4py.client.threadedclient import WebSocketClient # trim the fat, import only one class
import datetime
import sys
import hashlib
import os

class WebsocketRecorder(WebSocketClient):
        """ This class inherits from WebSocketClient class. We extend the __init__ method a bit. """
        def __init__(self, url, msg_to_send, max_lines, script_filename, machine_id, ws_name, field_separator):
                self.url = url
                self.msg_to_send = msg_to_send
		self.max_lines = max_lines 
                self.recorder_version = self.md5sum(script_filename)
                self.machine_id = machine_id
                self.pid = str(os.getpid())
                self.ws_name = ws_name
                self.fs = field_separator
                self.recorder_session_id = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f UTC")
                self.datafile = open(self.new_filename(), "a")
                self.datafile_lines_counter = 0
                try:
                        if len(extra_meta_data) > 0:
                                self.extra_meta_data = extra_meta_data
                except:
                        self.extra_meta_data = []

                super(WebsocketRecorder, self).__init__(self.url)
                
        def new_filename(self):
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
                filename = timestamp + "_" + self.ws_name + "_" + self.machine_id + ".tsv"
                return(filename)

        def opened(self):
                # Send initial messages to the websocket
                for message in self.msg_to_send:
                        self.send(message)
                 
        def closed(self, code, reason=None):
                # This method is called if the websocket connection is closed
                # deliberately by server or because of a connection error
                exit_message = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f UTC, ")\
                        + "Recorder stopped. Code: " + str(code) + ". Reason: " + str(reason) + "\n"
		print(exit_message) # gets printed into the log
                self.datafile.write(exit_message)
                self.datafile.close()

        def received_message(self, ws_msg):
                # Called when a WebSockets message is received. We write one message
                # per line. In addition to the WebSockets message, some other meta
                # info is written too.
                
                message = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f UTC")\
                        + self.fs + str(ws_msg) + self.fs\
                        + self.recorder_version + self.fs + self.machine_id\
                        + self.fs + self.recorder_session_id + self.fs\
                        + self.url + self.fs + self.pid

                # If the config file contained additional custom data
                # add it at the end of the message:
                if len(self.extra_meta_data) > 0:
                        for element in self.extra_meta_data:
                                message = message + self.fs + element

                # finally end the message with a newline
                message = message + "\n" 

                self.datafile.write(message)                
                self.datafile_lines_counter += 1

                # Check if the current data file became too big and we need to open new file.
                # One is one line line and is about 1KB. If log reaches max_lines 
                # start writing to new datafile
                if self.datafile_lines_counter >= self.max_lines:
                        self.datafile.close() # close the full datafile
                        self.datafile = open(self.new_filename(), 'a') # and open a new one
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
        
        # Load the settings specific to a particular websocket source.
        # The settings ar stored as Python variables.
        execfile(settings_file) 

        sys.stdout = open(stdout_file, "a")
        sys.stderr = open(stderr_file, "a")
        recorder = WebsocketRecorder(url, msg_to_send, max_lines, script_filename, machine_id, ws_name, field_separator)
        recorder.connect()
        recorder.run_forever()
