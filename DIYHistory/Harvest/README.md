## Harvesting Transcriptions from DIYHistory

REQUIRES [pycdm](http://github.com/saverkamp/pycdm) Python library to be installed   

Transcriptions (from any page modified in the past month) are automatically harvested from MySQL on the 25th via the **getTranscriptions.py** script and are checked against current CONTENTdm data with the **preCatcherDataChecks.py** script.  

**getTranscriptions.py** -- A script to harvest transcriptions from DIYHistory Omeka MySQL server. Reads in a logfile.csv to determine last date of harvest and writes current date minus one day back to logfile.csv. Connects to db and fetches transcriptions for any file modified since last harvest date. Writes transcriptions to a csv file piped to stdout. (Cron job pipes stdout to a tempfile.csv file, which is renamed and moved by preCatcherDataChecks.py)

**preCatcherDataChecks.py** -- Our only reliable point of reference between the DIYHistory pages and CDM pages is the page label (identifiers can be changed in CDM, so this is not a reliable identifier). This script reads in tempfile.csv and checks each DIYHistory page title listed against the CDM page label via the CDM API. Any mismatches are output into **updates_[timestamp].csv** Outputs two files:
* **CatcherUpload_OmekaTranscriptions[timestamp].csv** is the file that will eventually get uploaded to CONTENTdm via Catcher 
* **updates_[timestamp].csv** is a file of conflicting data that we need to spotcheck and manually clean up before we start the CONTENTdm upload.  

**logfile.csv** -- This file records the last harvest date.  

**CDMnickKey.csv** -- This file is a key to track CDM transcription field nicknames for each collection. If new collections are added to DIYHistory, the collection alias and field nickname for the full text (or 'transcription') field MUST be added to this file. Find the nickname for the full text field (or the field you want to put the transcription in) in the AllCollectionFields csv file (currently in the Catcher folder on CDM server), and add this nickname plus the collection alias to CDMnickKey.csv.  

Instructions for uploading to CDM via Catcher are in **Uploading_Transcriptions_to_CONTENTdm_from_DIYHistory.docx** and scripts are in **cdm-hacks/Catcher**