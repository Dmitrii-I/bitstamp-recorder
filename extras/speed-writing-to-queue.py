
from multiprocessing import Queue
from time import time

if __name__ == "__main__":

    num_messages = 1000000

    print('Testing how long it takes to add %s simple messages to a multiprocessing.Queue' % num_messages)
    queue_1 = Queue()

    t0 = time()
    for i in range(num_messages):
        queue_1.put(i)
    print(time() - t0)

    print('Testing how long it takes to add %s timestamp messages to a multiprocessing.Queue' % num_messages)
    queue_2 = Queue()

    t1 = time()
    for i in range(num_messages):
        queue_2.put(time())
    print(time() - t1)


