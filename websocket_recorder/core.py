""" Record incoming messages from a websocket endpoint.

Each websockets message is augmented and then written to a, optionally compressed JSON-lines datafile.
The augmented message consists of the original websocket message and meta data. Examples of meta data are the timestamp
when the message was received, or the hostname of the computer on which the recorder is running.
"""

from logging import getLogger
from ws4py.client.threadedclient import WebSocketClient
from datetime import datetime
from os.path import basename
from os import getpid
from json import dumps
from os import rename


log = getLogger(__name__)


class WebsocketRecorder(WebSocketClient):
    def __init__(self, data_dir, url, initial_msg_out, hostname, ws_name, hb_seconds, extra_data):
        """
        :param data_dir: the directory where to write the datafiles to. No trailing slash
        :param url: url of websocket
        :param initial_msg_out: list of messages to send to the endpoint upon opening connection
        :param hostname: the name of the local machine
        :param ws_name: name of the websocket endpoint
        :param hb_seconds: heartbeat interval
        :param extra_data: dictionary with additional data to add to each received websocket message
        :return: Reference to the WebsocketRecorder object
        """

        log.info("Initialize WebsocketRecorder, process pid=%s" % getpid())

        self.url = url
        self.initial_msg_out = initial_msg_out
        self.lines_counter = 0
        self.ws_name = ws_name
        self.hostname = hostname
        self.data_dir = data_dir
        self.data_file = open(self.generate_filename() + '.open', 'a')
        self.msg_seq_no = 0

        self.augmented_message = dict(
            url=self.url,
            machine_id=self.hostname,
            pid=str(getpid()),
            ws_name=self.ws_name,
            session_start=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f UTC")
        )

        if len(extra_data) > 0:
            self.augmented_message.update(extra_data)

        log.info("Augmented message template set to: %s" % self.augmented_message)

        super().__init__(url, heartbeat_freq=hb_seconds)

    def get_msg_seq_no(self):
        """ since no check is done if we exceed sys.maxint, there will be an exception
        once the msg_seq_no exceeds 2,147,483,647 (32-bit) or 9,223,372,036,854,775,807 (64-bit)
        """

        self.msg_seq_no += 1
        return self.msg_seq_no

    def generate_filename(self):
        extension = '.jsonl'
        date_part = datetime.now().strftime("%Y-%m-%dT%H")

        filename = self.data_dir + "/" + date_part + "_" + self.ws_name + "_" + self.hostname + extension

        log.info("Generated filename %s" % filename)
        return filename

    def opened(self):
        log.info("WebSocket %s connection to %s opened" % (self.ws_name, self.url))
        if len(self.initial_msg_out) > 0:
            log.info("Sending initial messages ...")
            for message in self.initial_msg_out:
                log.debug("Sending message: %s" % str(message))
                self.send(message)

    def closed(self, code, reason="not given"):
        log.info("WebSocket connection closed, code: %s, reason: %s" % (code, reason))
        self.data_file.close()

    def received_message(self, message):
        self.augmented_message['msg_seq_no'] = self.get_msg_seq_no()
        self.augmented_message['ts_utc'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f UTC')
        self.augmented_message['message'] = str(message).replace("\n", "")

        if self.augmented_message['ts_utc'][0:13] != basename(self.data_file.name)[0:13]:
            log.info("new hour, start new datafile")
            self.data_file.flush()
            self.data_file.close()
            rename(self.data_file.name, self.data_file.name.replace('.open', ''))
            self.data_file = open(self.generate_filename() + '.open', 'a')

        self.data_file.write(dumps(self.augmented_message, sort_keys=True) + '\n')
