from multiprocessing import Pipe
from time import time


if __name__ == "__main__":

    t0 = time()
    recv_conn, send_conn = Pipe(False)

    print('Put 1 million message into pipe.')
    for i in range(4096):
        send_conn.send(time())
        print('sent message %s' % i)
    print('Done')

    print('Fetch all the messages from the pipe')
    messages = []
    while recv_conn.poll():
        #print('fetched message')
        messages.append(recv_conn.recv())

    print('Fetched %s messages.' % len(messages))
    print(time() - t0)
