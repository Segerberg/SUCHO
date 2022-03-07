# DSpace OAI-PMH harvester and media downloader

These two tools can be used to download DSpace repos. 

## Installation

Preferably in a venv 

<pre>
pip install -r requirements.txt
</pre>

## oai_harvester.py
Used to download all records in METS format. 

<pre>
python oai_harvester.py --url http://dspace.domain.ua/oai/request --output-dir /path/to/somewhere
</pre>

The script will first try to download all record from "List of records" of an DSpace repo. If this fails it will try 
to grab the records from the "List of Sets". 

Each record will be saved into a subdirectory in the **--output-dir** named after the oai/record/header/identifier
If Sets are available they will be saved to a subdirectory named **sets**  


## dspace_download.py
Used to download all resources referenced in the METS files downloaded with **oai_harvester.py** 

<pre>
python dspace_download.py /path/to/dir 
</pre>

The script has an optional flag **--replace** or short **-r** which can be used to fix faulty domainnames of the often poorly configured 
DSpaces OAI-PMH endpoints 

<pre>
python dspace_download.py /path/to/dir -r http://localhost:8081 -r proper.domain:8081
</pre>  

## dspace_ia.py
Used to generate a list of all records and media links.
The script also attempts to get links for the start page and the startpages navigation links.
The script takes a single argument (url) which should point to the oai endpoint. like so http://mtom.pgasa.dp.ua/oai 
use > to pipe the output to a .txt
<pre>
python dspace_ia.py http://mtom.pgasa.dp.ua/oai > output.txt
</pre>