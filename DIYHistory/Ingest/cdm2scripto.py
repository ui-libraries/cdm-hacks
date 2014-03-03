#!/usr/bin/python

# cdm2scripto.py -- Pulls metadata from CDM through API and generates DIYHistory import csv files.
# This script takes in a collection alias or collection alias and CDM item ids, fetches relevant
# item-level and page-level metadata and generates two csv files ready for DIY import using mappings
# from https://github.com/ui-libraries/plugin-Scripto:
# * item.csv -- csv file of item-level metadata to be uploaded first.
# * file.csv -- csv file of page-level metadata to be uploaded after item.csv

# Author: Shawn Averkamp
# Last modified: 2014-02-24 

import re
import codecs
import csv
import datetime
import pycdm
from HTMLParser import HTMLParser
import os
import urllib2
#import requests

#select collection or items
choice = raw_input('fetch metadata by collection (c) or item id (i)? Enter c or i: ')

#get input: alias + items to retrieve
if choice == 'i':
    alias = raw_input('collection alias: ')
    items = raw_input('item identifiers (separate by commas): ')
    ptrs = items.split(',')

elif choice == 'c':
    alias = raw_input('collection alias: ')
    call = pycdm.Api()
    items = call.dmQuery('0', alias=alias, maxrecs='10000')
    ptrs = [i[1] for i in items]

#current date-time for output filenames
today = datetime.datetime.now().strftime('%Y-%m-%d--%H-%M')

#create file-level metadata csv file
fileOutput = alias + today + '_File.csv'
fFile = codecs.open(fileOutput, 'wb', encoding='utf_8')
wtrFile = csv.writer(fFile, delimiter=',')
#header row for file-level csv file
fileHeaderRow = ['filename', 'title', 'identifier', 'source', 'status', 'transcription', 'Omeka file order']
wtrFile.writerow(fileHeaderRow)

#create item-level metadata csv file
itemOutput = alias + today + '_Item.csv'
fItem = codecs.open(itemOutput, 'wb', encoding='utf_8')
wtrItem = csv.writer(fItem, delimiter=',')
#header row for item-level csv file
itemHeaderRow = ['title', 'identifier', 'source', 'ispartof', 'relation', 'audience', 'files']
wtrItem.writerow(itemHeaderRow)

#get data for each item
for ptr in ptrs:
    #call api for item metadata
    item = pycdm.item(alias, ptr, 'on')
    #set item-level metadata
    itemID = alias + '_' + ptr
    source = 'http://digital.lib.uiowa.edu/cdm/ref/collection/' + alias + '/id/' + ptr
    itemtitle = item.info['title']
    #digital collection url
    ispartof = 'http://digital.lib.uiowa.edu/' + alias
    sort = '000000'
    #collection guide url
    if ('findin' in item.info):
        relation = item.info['findin']
    elif ('collea' in item.info):
        relation = item.info['collea']
    else:
        relation = ''
    #setup for file data
    fileBaseURL = 'http://digital.lib.uiowa.edu/utils/getfile/collection/'
    files = []
    order = 1
    # dropbox base url
    dropbox = 'http://diyhistory.lib.uiowa.edu/transcribe/plugins/Dropbox/files'
    # temp directory for downloaded jpgs
    tempdir = 'dropbox'
    if not os.path.isdir(tempdir):
        os.mkdir(tempdir)
    #set file-level metadata
    for page in item.pages:
        fileID = itemID + '_' + page.id
        pagelabel = page.label
        pageRefURL = page.refurl
        #set transcription
        if (('full' in page.info) and page.info['full']):
            transcription = str(page.info['full'].encode('ascii', 'ignore'))
            transcription = HTMLParser().unescape(transcription)
        elif (('fula' in page.info) and page.info['fula']):
            transcription = str(page.info['fula'].encode('ascii', 'ignore'))
            transcription = HTMLParser().unescape(transcription)
        else:
            transcription = ''
        #skip if 'n/a' in transcription field
        if ((alias == 'cwd') and re.match('n/a', transcription.encode('ascii', 'ignore'))):
            pass
        else:
            #set transcription status
            if (transcription == ''):
                status = 'Not Started'
            elif ((alias == 'cwd') and re.match('reviewed', str(page.info['transc']))):
                status = 'Completed'
            else:
                status = 'Needs Review'
            # code below is for downloading JPEG2000s and generating url locations for where
            # they'll be manually moved before uploading to server. 
            if page.file[-3:] == 'jp2':
            # download image to temp directory (downloads locally, move these to 
            # plugins/dropbox/files on server)
                call = pycdm.Api()
                imagepath = call.GetImage(alias, page.id, scale='50')
                imagefile = alias + '_' + page.file.replace('jp2', 'jpg')
                imagedata = urllib2.urlopen(imagepath).read()
                tempfile = open(tempdir + '/' + imagefile, 'wb')
                tempfile.write(imagedata)
                url = dropbox + '/' + imagefile
            else: 
                url = fileBaseURL + alias + '/id/' + page.id + '/filename/' + page.file
            files.append(url)
            #write file metadata to file-level csv file
            filerow = [url, pagelabel, fileID, pageRefURL, status, transcription.encode('ascii', 'ignore'), order]
            wtrFile.writerow(filerow)
            order += 1
    #write item metadata to item-level csv file
    files = ','.join(files)
    itemrow = [itemtitle, itemID, source, ispartof, relation, sort, files]
    wtrItem.writerow(itemrow)
    print ptr
fItem.close()
fFile.close()
