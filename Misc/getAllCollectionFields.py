#!/usr/bin/python

# getAllCollectionFields.py -- Generates a csv file of all CONTENTdm collection field information.
# This script uses the CONTENTdm API to pull the list of all collections, then iterates through
# each collection, outputting a collection field per rown, including field label, field nickname,
# corresponding DC field, and other field properties. Outputs a csv file.

import pycdm
import csv
import datetime

#calculate current date-time for output filename
today = datetime.datetime.now().strftime('%Y-%m-%d--%H-%M')

#set up csv file
output = 'AllCollectionFields-' + today + '.csv'
f = open(output, 'wb')
wtr = csv.writer(f, delimiter=',')
#header row 
header = ['alias', 'field_nick', 'field_label', 'dc', 'required', 'searchable', 'vocabulary', 'hidden']
wtr.writerow(header)

#create an Api instance
call = pycdm.Api()

#get list of all collections
collectionslist = call.dmGetCollectionList()

#iterate through collection list, writing field data to csv for each collection field
for c in collectionslist:
    coll = pycdm.Collection(c['alias'].lstrip('/'))
    alias = coll.alias
    for k, v in coll.fields.items():
        nick = v.nick
        label = v.name
        dc = v.dc
        req = v.req
        search = v.search
        vocab = v.vocab
        hidden = v.hide
        row = [alias, nick, label, dc, req, search, vocab, hidden]
        wtr.writerow(row)

f.close()
