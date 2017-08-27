import gzip
from multiprocessing import Process, set_start_method
from time import time, sleep
from sqlite3 import connect

#set_start_method('fork')


class Datafile:
    def __init__(self, datafile_path):
        self.datafile_path = datafile_path
        self.conn = connect(':memory:')
        self.cursor = self.conn.cursor()
        print(self.cursor)
        self.cursor.execute("create table queue (message text not null)")
        self.conn.commit()

        self.writer = DatafileWriter(kwargs={'sqlite_conn': self.conn, 'datafile_path': self.datafile_path})
        self.writer.daemon = True
        self.writer.start()

    def enqueue(self, message):
        self.cursor.execute('insert into queue values (?)', (message,))
        self.conn.commit()


class DatafileWriter(Process):

    def run(self):

        cursor = self._kwargs['sqlite_conn'].cursor()
        print(cursor)
        while True:
            max_row_id = cursor.execute("select max(rowid) from queue").fetchall()[0][0]
            print('max rowid = %s' % max_row_id)
            print(cursor.execute('select count(*) from queue').fetchone()[0])

            if not max_row_id:
                sleep(3)
                continue

            cursor.execute('select * from queue where rowid <= ? order by rowid', (max_row_id,))
            rows = cursor.fetchall()

            if rows:

                print(len(rows))
                print(rows[0][0], rows[-1][0])

                self.write_to_disk(rows)
            else:
                print('No rows')

            sleep(3)

    def write_to_disk(self, rows):
        datafile_path = self._kwargs['datafile_path']
        with gzip.open(datafile_path, 'ab') as gzip_file:
            for message in rows:
                gzip_file.write((message[0] + '\n').encode('utf-8'))


if __name__ == "__main__":

    df = Datafile('/tmp/test-multiprocessing-sqlite.txt.gz')

    for i in range(100):
        df.enqueue(time())

    print(df.cursor.execute('select count(*) from queue').fetchone()[0])
    sleep(5)

    for i in range(100):
        df.enqueue(time())
    print(df.cursor.execute('select count(*) from queue').fetchone()[0])

    sleep(5)


