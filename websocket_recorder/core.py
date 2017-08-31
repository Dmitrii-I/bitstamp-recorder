""" Record incoming messages from a websocket endpoint.

Each websockets message is augmented and then written to a compressed JSON lines file. The augmented message
consists of the original websocket message and meta data. Examples of meta data are the timestamp when the message
was received, or the hostname of the computer on which the recorder is running.
"""


import gzip

from logging import getLogger
from multiprocessing import Pipe, Process, Queue
from ws4py.client.threadedclient import WebSocketClient
from datetime import datetime
from os.path import basename
from os import getpid
from json import dumps
from queue import Empty
from time import sleep


log = getLogger(__name__)


class _UncompressedDataFile:
    def __init__(self, datafile_path):
        self.path = datafile_path
        self._datafile = open(self.path, 'a')

    def append(self, message):
        self._datafile.write(message)

    def close(self):
        self._datafile.close()


class _CompressedDataFile:
    """ This private class represents a compressed datafile. Messages are flushed to disk once the buffer is full."""

    def __init__(self, datafile_path):
        self.path = datafile_path
        self.name = basename(self.path)
        self.pipe = Pipe(False)
        self.recv_conn, self.send_conn = self.pipe

        self.gzip_writer = Process(target=self._write_pipe_to_disk, args=(self.pipe, self.path))
        self.gzip_writer.start()
        log.info('Logging into %s using process with pid %s' % (self.path, self.gzip_writer.pid))

        self.recv_conn.close()

    @staticmethod
    def _write_pipe_to_disk(pipe, datafile_path):
        recv_conn, send_conn = pipe
        send_conn.close()

        messages_buffer = b''
        max_buffered_messages = 10000
        buffer_counter = 0

        def _write_to_gzip_file(blob):
            with gzip.open(datafile_path, 'ab') as gzip_file:
                gzip_file.write(blob)
                gzip_file.flush()

        while True:
            try:
                message = str(recv_conn.recv())

                if message == '\x04':
                    print('End of transmission')
                    _write_to_gzip_file(messages_buffer)
                    print('Done writing final chunk')
                    break

                messages_buffer += message.encode('utf-8')
                buffer_counter += 1

                if buffer_counter >= max_buffered_messages:
                    print('buffer full, writing to gzip')
                    _write_to_gzip_file(messages_buffer)
                    messages_buffer = b''
                    buffer_counter = 0

            except EOFError:
                print('Received EOF')
                # sleep(1)
                _write_to_gzip_file(messages_buffer)
                break

    def append(self, message):
        self.send_conn.send(message)

    def close(self):
        self.append('\x04')


class _CompressedDataFile2:
    """ This private class represents a compressed datafile. Messages are flushed to disk once the buffer is full."""

    def __init__(self, datafile_path):
        self.path = datafile_path
        self.name = basename(self.path)
        self.queue = Queue()

        self.gzip_writer = Process(target=self._write_queue_to_disk, args=(self.queue, self.path))
        self.gzip_writer.start()
        log.info('Logging into %s using process with pid %s' % (self.path, self.gzip_writer.pid))

    @staticmethod
    def _write_queue_to_disk(queue, datafile_path):

        messages_buffer = b''

        def _write_to_gzip_file(blob):
            with gzip.open(datafile_path, 'ab') as gzip_file:
                gzip_file.write(blob)
                gzip_file.flush()

        while True:
            try:
                message = queue.get(True, 0.005)

                if message == '\x04':
                    print('End of transmission')
                    _write_to_gzip_file(messages_buffer)
                    print('Done writing final chunk')
                    break

                messages_buffer += str(message).encode('utf-8')
            except Empty:
                if len(messages_buffer) > 0:
                    _write_to_gzip_file(messages_buffer)
                    messages_buffer = b''

            sleep(30)

    def append(self, message):
        self.queue.put_nowait(message)

    def close(self):
        self.append('\x04')


class WebsocketRecorder(WebSocketClient):
    def __init__(self, data_dir, url, initial_msg_out, hostname, ws_name, hb_seconds, extra_data, compress=False):
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
        self.compress = compress

        if self.compress:
            self.data_file = _CompressedDataFile2(self.generate_filename())
        else:
            self.data_file = _UncompressedDataFile(self.generate_filename())

        self.msg_seq_no = 0

        self.augmented_message = dict(
            msg_seq_no=None,
            url=self.url,
            machine_id=self.hostname,
            pid=str(getpid()),
            ws_name=self.ws_name,
            session_start=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f UTC"),
            ts_utc=None,
            websocket_msg=None)

        if len(extra_data) > 0:
            self.augmented_message.update(extra_data)

        log.info("Augmented message template set to: %s" % self.augmented_message)

        super().__init__(url, heartbeat_freq=hb_seconds)

    def get_msg_seq_no(self):
        # since no check is done if we exceed sys.maxint, there will be an exception
        # once the msg_seq_no exceeds 2,147,483,647 (32-bit) or 9,223,372,036,854,775,807 (64-bit)
        self.msg_seq_no += 1
        return self.msg_seq_no

    def generate_filename(self):
        extension = '.json.gz' if self.compress else '.json'
        date_part = datetime.now().strftime("%Y-%m-%d")

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
        log.info("WebSocket connection closed, code: %s, reason: %s" %(code, reason))
        self.data_file.close()

    def received_message(self, message):
        log.debug("Received message: %s" % message)
        self.augmented_message['msg_seq_no'] = self.get_msg_seq_no()
        self.augmented_message['ts_utc'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f UTC')
        self.augmented_message['message'] = str(message).replace("\n", "")

        if self.augmented_message['ts_utc'][0:10] != basename(self.data_file.path)[0:10]:
            log.info("Rotate datafiles: close current datafile; open new datafile")
            self.data_file.close()

            if self.compress:
                self.data_file = _CompressedDataFile2(self.generate_filename())
            else:
                self.data_file = _UncompressedDataFile(self.generate_filename())

        self.data_file.append(dumps(self.augmented_message, sort_keys=True) + "\n")
