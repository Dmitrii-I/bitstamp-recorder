import gzip
from multiprocessing import Pipe, Process, set_start_method
from time import time, sleep


if __name__ == "__main__":

    # t0 = time()
    # recv_conn, send_conn = Pipe(False)
    #
    # print('Put 1 million message into pipe.')
    # for i in range(4096):
    #     send_conn.send(time())
    #     print('sent message %s' % i)
    # print('Done')
    #
    # print('Fetch all the messages from the pipe')
    # messages = []
    # while recv_conn.poll():
    #     messages.append(recv_conn.recv())
    #
    # print('Fetched %s messages.' % len(messages))
    # print(time() - t0)

    recv_conn, send_conn = Pipe(False)


    class DataFileWriter(Process):
        def __init__(self, datafile_path, recv_conn, **kwargs):
            super().__init__(**kwargs)
            self.datafile = open(datafile_path, 'w')
            self.recv_conn = recv_conn

        def run(self):
            print('Start receiving')
            sleep(5)
            while True:
                try:
                    msg = str(self.recv_conn.recv())
                    self.datafile.write(msg)
                    print('wrote msg %s' % msg)
                except EOFError:
                    print('connection closed')
                    self.datafile.flush()
                    self.datafile.close()


    class DataFile:
        def __init__(self, datafile_path, send_conn, recv_conn):
            self.writer = DataFileWriter(datafile_path, recv_conn, daemon=True)
            self.writer.start()
            self.send_conn = send_conn
            sleep(1)

    df = DataFile('/tmp/test-multiprocessing-pipe.txt.gz', send_conn, recv_conn)

    t0 = time()
    for i in range(10):
        df.send_conn.send(time())

    df.send_conn.close()

    df.writer.recv_conn.close()
    sleep(9)

    print(time()-t0)
