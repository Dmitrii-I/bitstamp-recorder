""" Test whether it is faster to append to a gzip file or regular file. """


from time import time, sleep
import multiprocessing
import gzip
import queue


NUM_MESSAGES = 1000000


if __name__ == "__main__":

    print('Start')
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
        def __init__(self, datafile_path, **kwargs):
            super().__init__(**kwargs)
            self.datafile_path = datafile_path
            self.message_queue = multiprocessing.Queue()
            self.messages_per_run = 1000000

        def run(self):
            print('Started')
            while True:
                print('sleep')
                sleep(10)
                self.write_queue_to_disk()

        def write_queue_to_disk(self):
            messages = b''

            counter = 0
            for i in range(self.messages_per_run):
                try:
                    message = self.message_queue.get_nowait()
                    counter += 1
                    message = message.encode('utf-8')
                    messages += message
                except queue.Empty:
                    print('empty queue')
                    break

            with gzip.open(self.datafile_path, 'ab') as gzip_file:
                gzip_file.write(messages)
            print('wrote %s messages' % counter)


    class DataFile:
        def __init__(self, datafile_path):
            self.datafile_path = datafile_path
            self.writer = DataFileWriter(datafile_path)
            self.writer.start()
            self.msg_counter = 0

        def write(self, message):
            self.writer.message_queue.put(message)
            self.msg_counter += 1

        def close(self):
            pass


    print('Write {} messages to gzip file using multiprocessing'.format(NUM_MESSAGES))
    t0 = time()
    datafile = DataFile('/tmp/test.json.gz')
    for i in range(NUM_MESSAGES):
        datafile.write('{}\n'.format(time()))
    sleep(30)
    print('Wrote {} messages in {} seconds'.format(datafile.msg_counter, time() - t0))
