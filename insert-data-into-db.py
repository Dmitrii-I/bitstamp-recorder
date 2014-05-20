#!/usr/bin/env python
import fnmatch
import os
import json
import psycopg2
import decimal

pattern="*bitstamp_data*"

def is_file_closed(filename):
        pipe = os.popen("lsof -f -- %s" % filename)
        num_lines = len(pipe.readlines())
        pipe.close()
        if num_lines < 1:
                return(True)
        else:
                return(False)


def files_to_process():
        files = []
        for file in os.listdir('.'):
                if fnmatch.fnmatch(file, pattern) and is_file_closed(file):
                        files.append(file)
        return(files)

def process_line(line):
        try:
                elements = line.split(',', 1)
                json_line = json.loads(elements[1])
                if json_line["event"] == 'trade':
                        insert_into_trades(line)
                elif json_line["event"] == 'data':
                        insert_into_book(line)
        except ValueError:
                pass
                 
        

def insert_into_trades(line):
        elements = line.split(',', 1)
        json_line = json.loads(json.loads(elements[1])["data"]) # read in only relevant json part
        timestamp = elements[0]
        price = json_line["price"]
        volume = json_line["amount"]
        bitstamp_trade_id = json_line["id"]
        db.execute("insert into trades values(%s, %s, %s, %s)", (timestamp, bitstamp_trade_id,  price, volume))
        
         
def insert_into_book(line):
        elements = line.split(',', 1)
        json_line = json.loads(json.loads(elements[1])["data"]) # read in only relevant json part
        
        timestamp = elements[0]
        bids = json_line["bids"]
        for i in xrange(len(bids)):
                for j in xrange(len(bids[i])):
                        bids[i][j] = float(bids[i][j])

        asks = json_line["asks"]
        for i in xrange(len(asks)):
                for j in xrange(len(asks[i])):
                        asks[i][j] = float(asks[i][j])
        

        db.execute("insert into book values(%s, %s, %s)", (timestamp, bids, asks))



if __name__ == '__main__':
        
        db_conn = psycopg2.connect(database="test", user="testuser", password="testpass", host="127.0.0.1", port="5432")
        db = db_conn.cursor() 

        for file in files_to_process():
                print "Going to process file: ", file
                fd = open(file, 'r')
                lines = fd.readlines()
                fd.close()
                for line in lines:
                        # print "Going to process line: "
                        # print line
                        process_line(line)

        db_conn.commit()
        db_conn.close()



