#!/usr/bin/python

# preCatcherDataChecks.py -- Our only reliable point of reference between the DIYHistory pages 
# and CDM pages is the page label (identifiers can be changed in CDM, so this is not a reliable 
# identifier). This script reads in tempfile.csv and checks each DIYHistory page title listed 
# against the CDM page label via the CDM API. Any mismatches are output into 
# "updates_[timestamp].csv" Outputs two files:
#
# * CatcherUpload_OmekaTranscriptions[timestamp].csv -- is the file that will eventually get 
#   uploaded to CONTENTdm via Catcher 
# * updates_[timestamp].csv -- is a file of conflicting data that we need to spotcheck and 
#   manually clean up before we start the CONTENTdm upload.  
#
# Author: Shawn Averkamp
# Last modified: 2014-02-25


import sys
errfilename = '/local/vol00/diyharvest/err.txt'
sys.stderr = open(errfilename,'ab')

import pycdm
import csv
import datetime
import os
from httplib import HTTP
from urlparse import urlparse


def UnicodeDictReader(str_data, encoding, **kwargs):
    csv_reader = csv.DictReader(str_data, **kwargs)
    # Decode the keys once
    keymap = dict((k, k.decode(encoding)) for k in csv_reader.fieldnames)
    for row in csv_reader:
        yield dict((keymap[k], v.decode(encoding)) for k, v in row.iteritems())

def getstatus(url):
    p = urlparse(url)
    h = HTTP(p[1])
    h.putrequest('HEAD', p[2])
    h.endheaders()
    return h.getreply()[0]

# get csv file
csvfile = open('/local/vol00/diyharvest/tempfile.csv', 'rb')
c = UnicodeDictReader(csvfile, encoding='utf-8')

# create csv file for transactions
today = datetime.datetime.now().strftime('%Y-%m-%d--%H-%M')
# fname = 'PreCatcherDataChecks_' + today + '.csv'
# f = open(fname, 'wb')
# fwtr = csv.writer(f)
# header = ['cdm_page_id', 'cdm_item_id', 'cdm_label', 'omeka_label', 'validated', 'omeka_url', 'cdm_url', 'cdm_status']
# fwtr.writerow(header)

#create csv file for updates
uname = '/local/vol00/diyharvest/Data/updates_' + today + '.csv'
u = open(uname, 'wb')
uwtr = csv.writer(u)
uheader = ['original_filename', 'omeka_id', 'Identifier', 'Source', 'cdm_page_id', 'cdm_item_id', 'cdm_label', 'omeka_label', 'omeka_url', 'cdm_url']
uwtr.writerow(uheader)

pagekey = {}
verified = 'false'

#for each page, check if still current in CDM by matching on page labels
for row in c:
    pageId = row['CDM_page'].split('_')[-1]
    fullItemId = row['CDM_item']
    itemId = row['CDM_item'].split('_')[-1]
    alias = row['CDM_item'].split('_')[0]
    omekaId = row['Omeka_page']
    verified = 'false'
    cdmLabel = ''
    cdmurl = 'http://digital.lib.uiowa.edu/cdm/ref/collection/%s/id/%s' %(alias, pageId)
    omekaurl = 'http://diyhistory.lib.uiowa.edu/transcribe/scripto/transcribe/%s/%s' %(row['Omeka_item'], row['Omeka_page'])
    #create a dictionary for storing items and their page ids, labels
    if fullItemId not in pagekey:
        item = pycdm.item(alias, itemId)
        pagekey[fullItemId] = {p.id: p.label for p in item.pages}
    #set cdmLabel to contentdm page label that corresponds to cdm page id. set to blank if no corresponding label
    try:
        cdmLabel = pagekey[fullItemId][pageId]
    except:
        cdmLabel = ''
    # check cdm page label matches omeka page
    if cdmLabel == row['Page_label']:
        verified = 'true'
        writerow = [row['CDM_page'], row['CDM_item'], cdmLabel, row['Page_label'], verified, omekaurl, cdmurl]
        # fwtr.writerow(writerow)

    # if not, check to see if page id has changed (if changed, it would likely be one of the highest values
    # of the item's page ids, so check the last 4 pages of sorted page ids for a page label match)
    else:
        if len(pagekey[fullItemId]) > 4:
            # starting with the last page, iterate through the last 4 page ids in the pagekey
            for r in range(-1, -5, -1):
                # if page label matches, create new cdm id and url and
                # write new metadata to update file
                if row['Page_label'] == sorted((int(k), v) for k, v in pagekey[fullItemId].items())[r][1]:
                    verified = 'update'
                    new_cdm_id = fullItemId + '_' + str(sorted((int(k), v) for k, v in pagekey[fullItemId].items())[r][0])
                    newurl = 'http://digital.lib.uiowa.edu/cdm/ref/collection/%s/id/%s' % (alias, str(sorted((int(k), v) for k, v in pagekey[fullItemId].items())[r][0]))
                    ogfilename = row['Original_filename']
                    urow = [ogfilename, omekaId, new_cdm_id, newurl, row['CDM_page'], row['CDM_item'], cdmLabel, row['Page_label'], omekaurl, cdmurl]
                    uwtr.writerow(urow)
                    break
            # if no matches found, set validation to 'false'
            else:
                verified = 'false'
                ogfilename = row['Original_filename']
                urow = [ogfilename, omekaId, '', '', row['CDM_page'], row['CDM_item'], cdmLabel, row['Page_label'], omekaurl, cdmurl]
                uwtr.writerow(urow)
                writerow = [row['CDM_page'], row['CDM_item'], cdmLabel, row['Page_label'], verified, omekaurl, cdmurl]
                # fwtr.writerow(writerow)
        # if item is less than 4 pages long, set validation to 'false'        
        else:
            verified = 'false'
            ogfilename = row['Original_filename']
            urow = [ogfilename, omekaId, '', '', row['CDM_page'], row['CDM_item'], cdmLabel, row['Page_label'], omekaurl, cdmurl]
            uwtr.writerow(urow)
            writerow = [row['CDM_page'], row['CDM_item'], cdmLabel, row['Page_label'], verified, omekaurl, cdmurl]
            # fwtr.writerow(writerow)


csvfile.close()
filename = '/local/vol00/diyharvest/Data/CatcherUpload_OmekaTranscriptions_' + today + '.csv'
#f = open(filename, 'wb')
os.rename('/local/vol00/diyharvest/tempfile.csv', filename)
#f.close()
u.close()
#os.system('mailReports.py')
