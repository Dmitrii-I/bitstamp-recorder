"""
multi_pipe.py
"""
from multiprocessing import Process, Pipe
from time import sleep, time
import gzip


if __name__ == '__main__':

    class DataFile:
        def __init__(self, datafile_path):
            self.datafile_path = datafile_path
            self.pipe = Pipe(False)
            self.recv_conn, self.send_conn = self.pipe

            self.gzip_writer = Process(target=self._write_pipe_to_disk, args=(self.pipe, self.datafile_path))
            self.gzip_writer.start()
            self.recv_conn.close()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.close()

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

                    messages_buffer += (message + '\n').encode('utf-8')
                    buffer_counter += 1

                    if buffer_counter >= max_buffered_messages:
                        print('buffer full, writing to gzip')
                        _write_to_gzip_file(messages_buffer)
                        messages_buffer = b''
                        buffer_counter = 0

                except EOFError:
                    print('Received EOF')
                    #sleep(1)
                    _write_to_gzip_file(messages_buffer)
                    break

        def write(self, msg):
            self.send_conn.send(msg)

        def close(self):
            self.write('\x04')


    t0 = time()
    n = 898332
    with DataFile('/tmp/test-multiprocessing-pipes.txt.gz') as df:
        for i in range(n):
            df.write(i)

    print("Sent %s numbers to Pipe() took %s seconds" % (n, (time()-t0)))
