#!/usr/bin/env python 
#
# This Python module records incoming messages from a websocket endpoint.
# Each message is logged on one line, in JSON format. The logged message
# consists of the original received message plus some meta data. Examples of
# meta data are the timestamp of receiving the received message, or the hostname.
#
# Tested only on Linux.
#
# Dependencies: ws4py, version 0.3.3. at least. 

from ws4py.client.threadedclient import WebSocketClient # trim the fat, import only one class
import datetime
import os
import json
import logging


logger = logging.getLogger('websocket_recorder')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(os.path.expanduser('~') + "/var/log/websocket_recorder/log.txt", encoding="utf-8")
formatter = logging.Formatter(
    fmt='%(asctime)s.%(msecs).03d\t%(levelname)s\t(%(threadName)-10s)\t%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)


class WebsocketRecorder(WebSocketClient):
    def __init__(self, url, initial_msg_out, datafile_lines, script_filename,
                 hostname, ws_name, hb_seconds, extra_data):
        """
        :param url: url of websocket
        :param initial_msg_out: list of messages to send to the endpoint upon opening connection
        :param datafile_lines: write this many lines to a datafile, then switch to new file
        :param script_filename:
        :param hostname: the name of the local machine
        :param ws_name: name of the websocket endpoint
        :param hb_seconds: heartbeat interval
        :param extra_data: dictionary with additional data to add to each received websocket message
        :return: Reference to the WebsocketRecorder object
        """

        logger.info("Initialized new WebsocketRecorder object")
        # A list of messages to be sent upon opening websocket connection. Typically these messages
        # are subscriptions to channels/events/data
        self.url = url
        self.initial_msg_out = initial_msg_out
        self.datafile_lines = datafile_lines
        self.datafile = open(self.generate_filename(ws_name, hostname), "a")
        self.lines_counter = 0
        self.ws_name = ws_name
        self.hostname = hostname

        # Each time a websocket message arrives, we write full_message to the datafile, on a single line.
        # Here we define parts of the full message that do not change when a websocket message
        # arrives
        self.full_message = dict(url=self.url,
                                 machine_id=self.hostname,
                                 pid=str(os.getpid()),
                                 ws_name=self.ws_name,
                                 session_start=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f UTC"),
                                 ts_utc=None,
                                 websocket_msg=None)
        if len(extra_data) > 0:
            self.full_message.update(extra_data)

        logger.info("The template for the full message set to: %s" % self.full_message)

        # Call the init methods of WebSocketClient class
        super(WebsocketRecorder, self).__init__(url, heartbeat_freq=hb_seconds)

    def generate_filename(self, ws_name, machine_id):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
        filename = timestamp + "_" + self.ws_name + "_" + self.hostname + ".json"
        logger.info("Generated filename %s" % filename)
        return(filename)

    def opened(self):
        logger.info("WebSocket %s connection opened" % self.ws_name)
        if len(self.initial_msg_out) > 0:
            logger.info("Sending initial messages ...")
            for message in self.initial_msg_out:
                logger.debug("Sending message: %s" %str(message))
                self.send(message)

    def closed(self, code, reason=None):
        logger.info("WebSocket connection closed, code: %s, reason: %s" %(code, reason))
        self.datafile.close()

    def received_message(self, websocket_msg):
        logger.debug("Received message: %s" % websocket_msg)
        self.full_message['ts_utc'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f UTC')
        self.full_message['websocket_msg'] = str(websocket_msg).replace("\n", "")

        self.datafile.write(json.dumps(self.full_message, sort_keys=True) + "\n")
        self.lines_counter += 1
        # Check if the current data file became too big and we need to open new file.
        # One is one line line and is about 1KB. If log reaches datafile_lines
        # start writing to new datafile
        if self.lines_counter >= self.datafile_lines:
            self.datafile.close() # close the full datafile
            self.datafile = open(self.generate_filename(self.ws_name, self.hostname), 'a')
            self.lines_counter = 0



