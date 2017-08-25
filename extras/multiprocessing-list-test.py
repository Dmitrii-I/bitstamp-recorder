from multiprocessing import Manager
from queue import Empty
from time import time

if __name__ == "__main__":

    print('Test shared list')

    m = Manager()

    shared_list = m.list()
    t0 = time()
    print('Put 1 million message into shared list.')
    for i in range(100000):
        shared_list.append(time())
    print('Done %s' % (time() - t0))

    print('Fetch all the messages from the shared list')
    t1 = time()
    messages = []

    while shared_list:
        messages.append(shared_list.pop(0))

    print('Fetched %s messages. %s' % (len(messages), time() - t1))

    t0 = time()
    print('Put 1 million message into shared list.')
    for i in range(100000):
        shared_list.append(time())
    print('Done %s' % (time() - t0))

    print('Fetch all the messages from the shared list')
    t1 = time()
    messages = []

    while shared_list:
        messages.append(shared_list.pop(0))

    print('Fetched %s messages. %s' % (len(messages), time() - t1))
