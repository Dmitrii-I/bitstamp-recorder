import gzip
from multiprocessing import Process, set_start_method
from time import time, sleep
from sqlite3 import connect

set_start_method('fork')


class Datafile:
    def __init__(self, datafile_path):
        self.datafile_path = datafile_path
        self.conn = connect(':memory:')
        self.cursor = self.conn.cursor()
        self.cursor.execute("create table queue (message text not null)")
        self.conn.commit()

        self.writer = DatafileWriter(self.cursor, self.datafile_path)
        self.writer.daemon = True
        self.writer.start()

    def write(self, message):
        self.cursor.execute('insert into queue values (?)', (message,))
        self.conn.commit()


class DatafileWriter(Process):
    def __init__(self, sqlite_cursor, datafile_path, **kwargs):
        super().__init__(**kwargs)
        self.datafile_path = datafile_path
        self.cursor = sqlite_cursor

    def run(self):
        while True:
            max_row_id = self.cursor.execute("select max(rowid) from queue").fetchall()[0][0]
            print('max rowid = %s' % max_row_id)

            if not max_row_id:
                sleep(3)
                break

            self.cursor.execute('select * from queue where rowid <= ? order by rowid', (max_row_id,))
            rows = self.cursor.fetchall()

            if rows:

                print(len(rows))
                print(rows[0][0], rows[-1][0])

                self.write_to_disk(rows)
            else:
                print('No rows')

            sleep(3)

    def write_to_disk(self, rows):
        with gzip.open(self.datafile_path, 'ab') as gzip_file:
            for message in rows:
                gzip_file.write((message[0] + '\n').encode('utf-8'))


if __name__ == "__main__":

    df = Datafile('/tmp/test-multiprocessing-sqlite.txt.gz')

    for i in range(100):
        df.write(time())

    sleep(5)

    for i in range(100):
        df.write(time())

    sleep(5)


