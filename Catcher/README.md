## Uploading Metadata to CONTENTdm with Catcher

HAL documentation at: https://groupshare.uiowa.edu/libraries/dls/crowdsourcing/Shared%20Documents/Uploading_Metadata_to_CONTENTdm_with_Catcher.docx  
Github scripts at: https://github.com/ui-libraries/cdm-hacks  
Production scripts at: s-lib012.lib.uiowa.ed/local/vol00/Content6/Website/public_html/catcher  
* **CatcherUpload.py** -- Python upload script 
* **config.ini** -- variables for SOAP connection. Insert CDM password and license key before using

1)      **PREPARE YOUR SPREADSHEET—**Your upload spreadsheet must follow these conventions:

* **Filename**: This must be a csv file that begins with "CatcherUpload_" You can follow this prefix with whatever name you wish.
* **Fields**: You can include whatever fields you want in your spreadsheet, but you must include these fields at minimum (field names are case-sensitive). Any other fields will be ignored by the script.:

	> **Alias:** This is the collection handle for the item you are editing (ex. ‘cwd’)

	> **CDM_page_id:** The CONTENTdm id of the record you are editing. Each parent item and child record have their own CONTENTdm id. If you don’t know how to find this, talk to Ellen. MAKE SURE you have the correct id or you will risk overwriting the wrong metadata!

	> **CDM_field:** The nickname of the field you are editing (not the field label you see in IDL!) You can find the nicknames for all fields in all collections in the Catcher directory on the CDM server. ("AllCollectionFields_[timestamp].csv") This file is regenerated once a month. If you’ve changed field configurations for a collection since the timestamp listed in the most recent AllCollectionFields file, ask Brian to regenerate a new file.

	> **Value:** This is the new metadata value for the field you wish to edit. This will overwrite whatever value is currently in the record.

* There is a sample spreadsheet in the Catcher directory called "Sample_Catcher_Upload.csv"

2)      **CHECK THAT RECORDS ARE NOT LOCKED**-- Check the collections you are editing to see if any contain locked records. Metadata in CONTENTdm cannot be updated if the record is locked. Unlock what you can before the next step to save yourself from reuploading failed uploads later.

3)      **UPLOAD TO CONTENTDM VIA CATCHER**—To avoid disruption to the CDM server, the Catcher script runs every evening (if there is a file available to upload).

* Put the "CatcherUpload_[your description]. csv" file on the CDM server in the Catcher directory. Later in the evening, the upload script will run, upload the transcriptions, then email Ellen a transaction report. (Talk to Brian if you’d like it emailed to others.) This report and the original upload file are moved to catcher/Completed folder after the upload is finished. 
* Check the report the next day to see if all transcriptions were uploaded successfully:

	> A **"Transaction ID:"** indicates that the transcription was uploaded successfully

	> **"Error detail:"** This item is currently locked" means that the item is locked in CONTENTdm and has not been uploaded.  You will need to unlock this item and reupload the transcriptions from this item.
	> **"No content—not uploaded"** indicates that there was no transcription in the transcription field to upload. Check the upload file to make sure there was a transcription to be uploaded.

	> **"Malformed or invalid URL"** indicates an error with the upload. This could be from a network interruption during the upload. The data itself is usually fine—just try reuploading the next day.

4)      **UNLOCK and RE-UPLOAD LOCKED ITEMS—**If there were errors because of locked pages or "malformed" data, unlock these items in CDM administration (if locked), re-index the collection, and re-upload **just these pages**. (You will need to create a new upload file with just the pages that weren’t uploaded.) Follow the instructions for step 3 until all pages are uploaded.

 

