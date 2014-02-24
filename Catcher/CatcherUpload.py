#!/usr/bin/python

# CatcherUpload.py -- adapted from https://gist.github.com/saverkamp/9198310
# Updates existing metadata records with CONTENTdm Catcher protocol. (Documentation at: 
# http://contentdm.org/help6/addons/catcher.asp). 
# ***requires SUDS, a third-party SOAP python client: https://fedorahosted.org/suds/***
#
# Given a CSV file with a minimum of four fields: Alias, CDM_id, CDM_field, and Value, this script updates
# one value per row and returns a csv log of transcactions. For file input, currently set to iterate
# through the current directory and process any csv files beginning with "CatcherUpload". Input and 
# transaction files are output to "Completed" directory with timestamp.
#
# Author: Shawn Averkamp
# Last modified: 2014-02-24 

from ConfigParser import SafeConfigParser
from suds.client import Client
import datetime
import csv
import os
import fnmatch

# set variables for SOAP connection--requires config.ini file
parser = SafeConfigParser()
parser.read('/local/vol00/Content6/Website/public_html/catcher/config.ini')
user = parser.get('catcher', 'cdmusername')
password = parser.get('catcher', 'cdmpass')
license = parser.get('catcher', 'cdmlicense')
base = parser.get('catcher', 'base')
pw = parser.get('catcher', 'cdmpass')
port = parser.get('catcher', 'port')
url = base + ":" + port

class Catcher(object):
    """A CONTENTdm Catcher session."""
    def __init__(self, url=url, user=user, password=password, license=license):
        self.transactions = []
        self.client = Client('https://worldcat.org/webservices/contentdm/catcher/6.0/CatcherService.wsdl')
        self.url = url
        self.user = user
        self.password = password
        self.license = license

    def processCONTENTdm(self, action, user, password, license, alias, metadata):
        # params = [action, url, user, password, license, alias, metadata]
        transaction = self.client.service.processCONTENTdm(action, url, user, password, license, alias, metadata)
        # strip extraneous warnings
        # transaction = transaction.split('\n')
        # transaction = transaction[0]
        self.transactions.append(transaction)

    def edit(self, alias, recordid, field, value):
        #package metadata in metadata wrapper
        metadata = self.packageMetadata('edit', recordid, field, value)
        self.processCONTENTdm('edit', self.user, self.password, self.license, alias, metadata)

    def packageMetadata(self, action, recordid, field, value):
        action = action
        if action == 'edit':
            metadata = self.client.factory.create('metadataWrapper')
            metadata.metadataList = self.client.factory.create('metadataWrapper.metadataList')
            metadata1 = self.client.factory.create('metadata')
            metadata1.field = 'dmrecord'
            metadata1.value = recordid
            metadata2 = self.client.factory.create('metadata')
            metadata2.field = field
            metadata2.value = value
            metadata.metadataList.metadata = [metadata1, metadata2]
        return metadata

def UnicodeDictReader(str_data, encoding, **kwargs):
    csv_reader = csv.DictReader(str_data, **kwargs)
    # Decode the keys once
    keymap = dict((k, k.decode(encoding)) for k in csv_reader.fieldnames)
    for row in csv_reader:
        yield dict((keymap[k], v.decode(encoding)) for k, v in row.iteritems())

if __name__ == "__main__":

    #iterate through current directory to find any files starting with 'CatcherUpload' and process
    for file in os.listdir('.'):
        if fnmatch.fnmatch(file, 'CatcherUpload*.csv'):
            csvfile = open(file, 'rb')
            c = UnicodeDictReader(csvfile, encoding='utf-8')

            # create directory for completed files and transaction logs if it doesn't exist
            newdir = '/local/vol00/Content6/Website/public_html/catcher/Completed'
            if not os.path.isdir(newdir):
                os.mkdir(newdir)

            # create csv file for transactions
            today = datetime.datetime.now().strftime('%Y-%m-%d--%H-%M')
            fname = '/local/vol00/Content6/Website/public_html/catcher/Completed/Transactions_' + file[0:-4] + '_' + today + '.csv'
            f = open(fname, 'wb')
            fwtr = csv.writer(f)
            header = ['Alias', 'CDM_id', 'CDM_field', 'Transaction']
            fwtr.writerow(header)

            #initialize Catcher session
            session = Catcher(password=pw)

            itemid = ''
            for row in c:
                # get values from row and package metadata for edits
                cdmid = row['CDM_page_id']
                alias = row['Alias']
                field = row['CDM_field']
                value = row['Value']
                # package metadata for Catcher and upload if value is not empty
                if value != '':
                    session.edit(alias, cdmid, field, value)     
                    # write transaction message to file
                    fRow = [alias, cdmid, field, session.transactions[-1]]
                else:
                    fRow = [alias, cdmid, field, 'No content--not uploaded']
                fwtr.writerow(fRow)

            f.close()
            csvfile.close()
            # append timestamp to upload csv filename and move to Completed directory
            newcsv = '/local/vol00/Content6/Website/public_html/catcher/Completed/' + file[0:-4] + '_' + today + '.csv'
            oldfile = '/local/vol00/Content6/Website/public_html/catcher/' + file
            os.rename(oldfile, newcsv)
