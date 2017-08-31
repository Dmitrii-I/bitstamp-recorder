from multiprocessing import Queue
from queue import Empty
from time import time

if __name__ == "__main__":

    print('Queue is too slow in making the messages available.')

    big_message = {'a': [1, 2, 3, 4, 5, 6], 'b': 4.444343434, 'c': 'lorem ipsum lorem ipsum lorem ipsum lorem ipsum',
                   'd': {'kekeke': 'kekekekeke', 'z': 555.55}, 'e': 'fvlkfvjkfjvlfjvfjklfsjlfkj', 'f': []}

    n = 1000000

    q = Queue()

    t0 = time()
    print('Put %s messages into queue.' % n)
    for i in range(n):
        q.put(big_message)
    print('Done %s' % (time() - t0))

    print('Fetch all the messages from the queue')
    t1 = time()
    messages = []
    while True:
        try:
            messages.append(q.get(True, 0.01))
        except Empty:
            break

    print('Fetched %s messages in %s.' % (len(messages), time() - t1))
    print('Failed to fetch %s messages because queue told us erroneously that it was empty' % (n - len(messages)))
