from multiprocessing import Queue
from queue import Empty
from time import time

if __name__ == "__main__":

    print('Queue is too slow in making the messages available.')

    q = Queue()

    print('Put 1 million message into queue.')
    for i in range(1000000):
        q.put(time())
    print('Done')

    print('Fetch all the messages from the queue')
    messages = []
    while True:
        try:
            messages.append(q.get_nowait())
        except Empty:
            pass
        if len(messages) > 999999:
            break

    print('Fetched %s messages.' % len(messages))

    print('Failed to fetch %s messages because queue told us erroneously that it was empty' % (1000000 - len(messages)))
