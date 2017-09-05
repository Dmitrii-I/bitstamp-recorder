from time import sleep, time
from multiprocessing import Pipe, Process
import gzip
import numpy as np
import os
from json import dumps, loads


def write_to_compressed_file_separate_process_using_pipes(pipe):
    recv_conn, send_conn = pipe
    send_conn.close()  # close send side, so that we can receive EOF exception

    with gzip.open('/tmp/test2.txt.gz', 'at') as gzip_file:
        while True:
            try:
                message = recv_conn.recv()

                if message == '\x04':
                    break

                gzip_file.write(message)

            except EOFError:
                break

        gzip_file.flush()


def write_to_compressed_file_separate_process_using_pipes_and_batches(pipe):
    recv_conn, send_conn = pipe
    send_conn.close()  # close send side, so that we can receive EOF exception

    with gzip.open('/tmp/test3.txt.gz', 'at') as gzip_file:

        buffer = ''
        buffer_msg_count = 0
        msg_per_batch = 1000

        while True:
            try:
                message = recv_conn.recv()

                if message == '\x04':
                    break

                buffer += message
                buffer_msg_count += 1

                if buffer_msg_count >= msg_per_batch:
                    gzip_file.write(message)
                    buffer_msg_count = 0
                    buffer = ''

            except EOFError:
                break

        gzip_file.flush()


def write_to_uncompressed_file_separate_process_using_pipes(pipe):
    recv_conn, send_conn = pipe
    send_conn.close()  # close send side, so that we can receive EOF exception

    with open('/tmp/test4.txt', 'w') as fd:
        while True:
            try:
                message = recv_conn.recv()

                if message == '\x04':
                    break

                fd.write(message)

            except EOFError:
                break

        fd.flush()


if __name__ == "__main__":

    big_message = {"key1": "a" * 3, "key2": "a" * 1000, "key3": 1000, "key5": None}

    n = 100000

    fd = open('/tmp/test1.txt', 'w')

    ####################################################################################################
    print('Write %s messages to %s in same thread' % (n, fd.name))
    for i in range(n):
        message = big_message
        message['ts'] = time()
        fd.write(dumps(message) + '\n')
    fd.close()

    timestamps = []
    with open('/tmp/test1.txt') as fd:
        for line in fd:
            parsed_line = loads(line)
            timestamps.append(parsed_line['ts'])

    x = np.array(timestamps)
    x = np.diff(x)
    x = np.mean(x)
    print('Wrote %s messages, 1 message per %s microseconds' % (n, x * 1000 * 1000))

    ####################################################################################################
    print('Test writing to datafile in separate process, passing messages through pipe')
    if os.path.exists('/tmp/test2.txt.gz'):
        os.remove('/tmp/test2.txt.gz')

    pipe = Pipe(False)
    recv_conn, send_conn = pipe

    writer = Process(target=write_to_compressed_file_separate_process_using_pipes, args=(pipe,))
    writer.start()
    recv_conn.close()  # close to release file descriptor, thereby allowing for EOF exceptions

    for i in range(n):
        message = big_message
        message['ts'] = time()
        send_conn.send(dumps(message) + '\n')
    send_conn.send('\x04')

    sleep(2)
    timestamps = []
    with gzip.open('/tmp/test2.txt.gz', 'rt') as fd:
        for line in fd:
            parsed_line = loads(line)
            timestamps.append(parsed_line['ts'])

    x = np.array(timestamps)
    x = np.diff(x)
    x = np.mean(x)
    print('Wrote %s messages, 1 message per %s microseconds' % (n, x * 1000 * 1000))

    ####################################################################################################
    print('Test writing to datafile in separate process, passing messages through pipe and write in batches')
    if os.path.exists('/tmp/test3.txt.gz'):
        os.remove('/tmp/test3.txt.gz')

    pipe = Pipe(False)
    recv_conn, send_conn = pipe

    writer = Process(target=write_to_compressed_file_separate_process_using_pipes_and_batches, args=(pipe,))
    writer.start()
    recv_conn.close()  # close to release file descriptor, thereby allowing for EOF exceptions

    for i in range(n):
        message = big_message
        message['ts'] = time()
        send_conn.send(dumps(message) + '\n')
    send_conn.send('\x04')

    sleep(2)
    timestamps = []
    with gzip.open('/tmp/test3.txt.gz', 'rt') as fd:
        for line in fd:
            parsed_line = loads(line)
            timestamps.append(parsed_line['ts'])

    x = np.array(timestamps)
    x = np.diff(x)
    x = np.mean(x)
    print('Wrote %s messages, 1 message per %s microseconds' % (n, x * 1000 * 1000))

    ####################################################################################################
    print('Test writing to uncompressed datafile in separate process using pipe')

    pipe = Pipe(False)
    recv_conn, send_conn = pipe

    writer = Process(target=write_to_uncompressed_file_separate_process_using_pipes, args=(pipe,))
    writer.start()
    recv_conn.close()  # close to release file descriptor, thereby allowing for EOF exceptions

    for i in range(n):
        message = big_message
        message['ts'] = time()
        send_conn.send(dumps(message) + '\n')
    send_conn.send('\x04')

    timestamps = []
    with open('/tmp/test4.txt', 'r') as fd:
        for line in fd:
            parsed_line = loads(line)
            timestamps.append(parsed_line['ts'])

    x = np.array(timestamps)
    x = np.diff(x)
    x = np.mean(x)
    print('Wrote %s messages, 1 message per %s microseconds' % (n, x * 1000 * 1000))
