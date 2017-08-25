import sqlite3
import multiprocessing as mp
from multiprocessing import Process, Queue


def get_a_stock(queue, cursor, symbol):
    cursor.execute("SELECT * FROM stocks WHERE symbol = '%s'" % symbol)
    queue.put(cursor.fetchall())


if __name__ == '__main__':
    """
    multiprocessing supports three ways to start a process, one of them is fork:
    The parent process uses os.fork() to fork the Python interpreter.
    The child process, when it begins, is effectively identical to the parent process.
    All resources of the parent are inherited by the child process.
    Note that safely forking a multithreaded process is problematic.
    Available on Unix only. The default on Unix.
    """
    mp.set_start_method('fork')

    conn = sqlite3.connect(":memory:")
    c = conn.cursor()

    # Create table
    c.execute('''CREATE TABLE stocks
                 (date text, trans text, symbol text, qty real, price real)''')

    # Insert a row of data
    c.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','USD',100,35.14)")

    # Save (commit) the changes
    conn.commit()

    q = mp.Queue()
    p = mp.Process(target=get_a_stock, args=(q, c, 'USD', ))
    p.start()
    result = q.get()
    p.join()

    for r in result:
        print(r)

    c.close()
    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()
