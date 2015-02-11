# This Python module records incoming messages from a websocket endpoint.
# Each message is logged on one line, in JSON format. The logged message
# consists of the original received webscket message plus some meta data. Examples of
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

# Setup logging. Override logging levels in your script that imports this module.
wsrec_logger = logging.getLogger('websocket_recorder')
wsrec_logger.setLevel(logging.DEBUG)
ws4py_logger = logging.getLogger('ws4py')
ws4py_logger.setLevel(logging.DEBUG)

handler = logging.FileHandler("/var/log/websocket_recorder/log.txt", encoding="utf-8")
formatter = logging.Formatter(
    fmt='%(asctime)s.%(msecs).03d\t%(levelname)s\t(%(threadName)-10s)\t%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)

wsrec_logger.addHandler(handler)
ws4py_logger.addHandler(handler)


class WebsocketRecorder(WebSocketClient):
    def __init__(self, data_dir, url, initial_msg_out, data_file_lines, hostname, ws_name, hb_seconds, extra_data):
        """
        :param data_dir: the directory where to write the datafiles to. No trailing slash
        :param url: url of websocket
        :param initial_msg_out: list of messages to send to the endpoint upon opening connection
        :param data_file_lines: write this many lines to a data_file, then switch to new file
        :param hostname: the name of the local machine
        :param ws_name: name of the websocket endpoint
        :param hb_seconds: heartbeat interval
        :param extra_data: dictionary with additional data to add to each received websocket message
        :return: Reference to the WebsocketRecorder object
        """

        wsrec_logger.info("Initialized new WebsocketRecorder object")
        # A list of messages to be sent upon opening websocket connection. Typically these messages
        # are subscriptions to channels/events/data
        self.url = url
        self.initial_msg_out = initial_msg_out
        self.data_file_lines = data_file_lines
        self.lines_counter = 0
        self.ws_name = ws_name
        self.hostname = hostname
        self.data_dir = data_dir
        self.data_file = open(self.generate_filename(), "a")

        # Each received websocket message is expanded to a full message and written on a single line.
        # Here we define parts of the full message that stay constant during recording session
        self.full_message = dict(url=self.url,
                                 machine_id=self.hostname,
                                 pid=str(os.getpid()),
                                 ws_name=self.ws_name,
                                 session_start=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f UTC"),
                                 ts_utc=None,
                                 websocket_msg=None)
        if len(extra_data) > 0:
            self.full_message.update(extra_data)

        wsrec_logger.info("The template for the full message set to: %s" % self.full_message)

        # Call the init methods of WebSocketClient class
        super(WebsocketRecorder, self).__init__(url, heartbeat_freq=hb_seconds)

    def generate_filename(self):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
        filename = self.data_dir + "/" + timestamp + "_" + self.ws_name + "_" + self.hostname + ".json"
        wsrec_logger.info("Generated filename %s" % filename)
        return filename

    def opened(self):
        wsrec_logger.info("WebSocket %s connection to %s opened" % (self.ws_name, self.url))
        if len(self.initial_msg_out) > 0:
            wsrec_logger.info("Sending initial messages ...")
            for message in self.initial_msg_out:
                wsrec_logger.debug("Sending message: %s" % str(message))
                self.send(message)

    def closed(self, code, reason="not given"):
        wsrec_logger.info("WebSocket connection closed, code: %s, reason: %s" %(code, reason))
        self.data_file.close()

    def received_message(self, websocket_msg):
        wsrec_logger.debug("Received message: %s" % websocket_msg)
        self.full_message['ts_utc'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f UTC')
        self.full_message['websocket_msg'] = str(websocket_msg).replace("\n", "")

        self.data_file.write(json.dumps(self.full_message, sort_keys=True) + "\n")
        self.lines_counter += 1
        if self.lines_counter >= self.data_file_lines:
            # close the full data_file
            self.data_file.close()
            self.data_file = open(self.generate_filename(), 'a')
            self.lines_counter = 0
