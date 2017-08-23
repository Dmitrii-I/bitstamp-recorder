""" Test whether it is faster to append to a gzip file or regular file. """


from time import time, sleep
import multiprocessing
import gzip
import queue


NUM_MESSAGES = 1000000


if __name__ == "__main__":

    # print('Start')
    # sleep(3)
    #
    # print('Write {} messages to regular file'.format(NUM_MESSAGES))
    # t0 = time()
    # with open('/tmp/test_append_regular.txt', 'w') as regular_file:
    #     for i in range(NUM_MESSAGES):
    #         regular_file.write('{}\n'.format(time()))
    # print('Wrote {} messages in {} seconds'.format(NUM_MESSAGES, time()-t0))
    #
    # print('Write {} messages to (different) regular file once again'.format(NUM_MESSAGES))
    # t0 = time()
    # with open('/tmp/test_append_regular2.txt', 'w') as regular_file:
    #     for i in range(NUM_MESSAGES):
    #         regular_file.write('{}\n'.format(time()))
    # print('Wrote {} messages in {} seconds'.format(NUM_MESSAGES, time() - t0))
    #
    # print('Write {} messages to gzip file'.format(NUM_MESSAGES))
    # t0 = time()
    # with gzip.GzipFile('/tmp/test_append_gzip.txt.gz', 'w') as gzip_file:
    #     for i in range(NUM_MESSAGES):
    #         gzip_file.write('{}\n'.format(time()).encode(encoding='utf-8'))
    # print('Wrote {} messages in {} seconds'.format(NUM_MESSAGES, time() - t0))


    class DataFileWriter(multiprocessing.Process):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.message_queue = multiprocessing.Queue()
            self.chunk_size = 1000000

        def run(self):
            while True:
                print('sleep')
                sleep(3)

                messages = []

                for i in range(self.chunk_size):
                    try:
                        messages.append(self.message_queue.get_nowait())
                    except queue.Empty:
                        break

                with gzip.open('/tmp/test_append_gzip_multiprocessing.txt.gz', 'ab') as gzip_file:
                    gzip_file.write(''.join(messages).encode('utf-8'))

                messages = []


    class DataFile:
        def __init__(self):
            self.writer = DataFileWriter()
            self.writer.start()
            self.msg_counter = 0

        def write(self, message):
                self.writer.message_queue.put(message)


    print('Write {} messages to gzip file using multiprocessing'.format(NUM_MESSAGES))
    t0 = time()
    datafile = DataFile()
    for i in range(NUM_MESSAGES):
        datafile.write('{}\n'.format(time()))
    print('Wrote {} messages in {} seconds'.format(NUM_MESSAGES, time() - t0))
