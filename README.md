# Political-Expression-in-Web-Defacements-Crawler
Preliminary repo for any scripts and software developed in the context of the thesis.


All files are explained in detail in the dissertation, here is a short overview:

### zoneH_IWL_GUI.py 
The GUI (really cli in a box) crawler for Zone-H. Requires a few empty csv files to be present, check code

### fill_rawtext.py 
Connects to SQL DB and writes text and metadata from scraped fiels to DB. See dissertation for DB structure

### sql_functions.py 
Connects to DB and cleans the imported data so it is ready for analysis

### analysis.py 
runs a range of analysis on the corpus, outputs can be saved to file or shown in the editor

### inScope.py 
Just a little help for moving files around

### ZoneHRandomCrawler 
variation of an earlier version of the crawler to select random IDs
