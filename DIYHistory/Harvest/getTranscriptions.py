#!/usr/bin/python

# getTranscriptions.py -- A script to harvest transcriptions from DIYHistory Omeka MySQL server.
# Reads in a logfile.csv to determine last date of harvest and writes current date minus one day
# back to logfile.csv. Connects to db and fetches transcriptions for any file modified since last
# harvest date. Writes transcriptions to a csv file piped to stdout. (Cron job pipes stdout to a
# tempfile.csv file) Outputs two files: “CatcherUpload_OmekaTranscriptions[timestamp].csv” is 
# the file that will eventually get uploaded to CONTENTdm via Catcher, “updates_[timestamp].csv” 
# is a file of conflicting data that we need to spotcheck and manually clean up before we start 
# the CONTENTdm upload.
#
# Be sure to populate database password in line 60 before using.
#
# Author: Shawn Averkamp
# Last modified: 2014-02-25

import MySQLdb as mysql
import csv
import getpass
import codecs
import datetime
import cStringIO
import os
import sys


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([unicode(s).encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

errfilename = 'err.txt'
sys.stderr = open(errfilename,'w')

#open db connection
# user = raw_input("Enter your db username: ")
# pw = getpass.getpass("Enter your db password: ")
# db = mysql.connect(db='omeka', host='128.255.52.153', user=user, passwd=pw, use_unicode=True, charset='utf8')
db = mysql.connect(db='omeka', user='omeka_user', passwd='', use_unicode=True, charset='utf8')
db.set_character_set('utf8')
c = db.cursor()
c.execute('SET NAMES utf8;')
c.execute('SET CHARACTER SET utf8;')
c.execute('SET character_set_connection=utf8;')


#create directory for transcriptions
datadir = 'Data'
if not os.path.isdir(datadir):
    os.mkdir(datadir)

#initialize csv file and writer
#current date-time for output filenames
today = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# filename = datadir + '/OmekaTranscriptions_' + today + '.csv'
# f = open(filename, 'wb')
#wtr = UnicodeWriter(f, delimiter=',', )
wtr = UnicodeWriter(sys.stdout, delimiter=',', )

#read in log file
logfilename = 'logfile.csv'
l = open(logfilename, 'rb')
logfile = csv.reader(l, delimiter=',')
loglines = [line for line in logfile]
lastline = loglines[-1]
lastdatetime = datetime.datetime.strptime(lastline[0], '%Y-%m-%d %H:%M:%S')
l.close()

#read in field nicknames key
n = open('CDMnickKey.csv', 'rb')
nicknamekeyfile = csv.DictReader(n, delimiter=',')
nicknamekey = {line['alias']: line['transcription_nick'] for line in nicknamekeyfile}

#header row
header = ['CDM_item', 'Omeka_item', 'CDM_page', 'Omeka_page', 'Title', 'Page_label', 'Value', 
'Original_filename', 'Alias', 'CDM_page_id', "CDM_field"]
wtr.writerow(header)

#set current datetime minus 1 day for logs
newlogdt = datetime.datetime.now()
newlogdt = newlogdt - datetime.timedelta(days=1)
newlogdt = newlogdt.strftime('%Y-%m-%d %H:%M:%S')

#set total files
totalfiles = 0
#check for files modified (expect where modification is adding new file) since last datetime in log
c.execute("""SELECT id FROM files WHERE modified > %s AND modified != added""", (lastdatetime,))
changedfiles = c.fetchall()
changedfiles = [changedfile[0] for changedfile in changedfiles]

d = db.cursor()
d.execute('SET NAMES utf8;')
d.execute('SET CHARACTER SET utf8;')
d.execute('SET character_set_connection=utf8;')
for cf in changedfiles:
    d.execute("""SELECT text FROM element_texts WHERE record_id = %s AND element_id = '137'""" %cf)
    status = d.fetchall()
    if status:
        status = [s[0] for s in status][0]
        if status != 'Not Started':
            #get parent item
            d.execute("""SELECT item_id FROM files WHERE id = %s""" %cf)
            itemId = d.fetchall()
            itemId = [iId[0] for iId in itemId][0]

            #get CDM item id
            d.execute("""SELECT text FROM element_texts WHERE record_id = %s AND record_type_id = '2' AND element_id = '43'""" %itemId)
            CDMitemId = d.fetchall()
            if CDMitemId:
                CDMId = [cId[0] for cId in CDMitemId][0]
            else:
                CDMId = ''
            # get item title
            d.execute("""SELECT text FROM element_texts WHERE record_id = %s AND element_id = '50'""" %itemId)
            itemTitle = d.fetchall()
            itemTitle = [t[0] for t in itemTitle][0]

            # get CDM page id
            try:
                d.execute("""SELECT text FROM element_texts WHERE record_id = %s AND record_type_id = '3' AND element_id = '43'""" %cf)
                pageId = d.fetchall()
                if pageId:
                    pageId = [pId[0] for pId in pageId][0]
                else:
                    pageId = ''
            except:
                pageId = ''
            # get page label
            d.execute("""SELECT text FROM element_texts WHERE record_id = %s AND element_id = '50'""" %cf)
            pageLabel = d.fetchall()
            if pageLabel:
                pageLabel = [pl[0] for pl in pageLabel][0]
            else:
                pageLabel = ''
            # get transcription
            d.execute("""SELECT text FROM element_texts WHERE record_id = %s AND element_id = '136'""" %cf)
            transc = d.fetchall()
            try:
                transc = [tr[0] for tr in transc][0]
            except IndexError:
                transc = ''
            # get original filename
            d.execute("""SELECT original_filename FROM files WHERE id = %s""" %cf)
            ogfilename = d.fetchall()
            ogfilename = [fn[0] for fn in ogfilename][0]
            #CDM alias and page id
            CDMalias = pageId.split('_')[0]
            CDMpageId = pageId.split('_')[-1]
            #get transcription field nickname for alias, error sent to err.txt if nickname not in key
            field_nick = ''
            if CDMalias in nicknamekey:
                field_nick = nicknamekey[CDMalias]

            #output row
            row = [CDMId, str(itemId), pageId, str(cf), itemTitle, pageLabel, transc, ogfilename, CDMalias, CDMpageId, field_nick]
            wtr.writerow(row)
            totalfiles += 1

logline = str(newlogdt) + ',' + str(totalfiles) + '\n'
l = open('logfile.csv', 'ab')
l.write(logline)
l.close()
n.close()
