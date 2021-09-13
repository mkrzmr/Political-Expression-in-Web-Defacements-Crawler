#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 16:16:07 2020
# connecting to local mysql database and filling in the raw text
@author: Michael Kurzmeier
"""

import glob2
import sqlalchemy
from sqlalchemy import text
from bs4 import BeautifulSoup

filenames = glob2.glob('*.txt')

engine = sqlalchemy.create_engine('mysql://michael:t"!tnm2Y]"@127.0.0.1/mydb', encoding='utf-8') # make sure encodign in DB is binary
db = engine.connect()

#print(filenames)
def fill_raw_text(): #loads all text files and inserts them into database
    for i in filenames:
        with open(i, 'rb') as infile:
            html = infile.read()
            defid = i[:-4]
            sql = text('INSERT INTO raw_text VALUES (:defid, :msg)')
            db.execute(sql, defid=defid, msg=html)
    db.close()
    
def fill_clean_text(): #loads all raw_html fields, strips away html tags and writes output to clean_text
 
    sql = ('SELECT DefacementId, raw_html FROM mydb.raw_text;')
    for row in db.execute(sql):
        defid = row[0]
        raw_html=str(row[1]) # now all data is turned into a string again
        soup = BeautifulSoup(raw_html,"html5lib")
        clean = soup.get_text(strip=True) #strip away html tags
        clean =clean.encode()
        sql = text ('UPDATE `mydb`.`raw_text` SET `clean_text` = :clean WHERE (`DefacementId` = :defid);')
        db.execute(sql, clean=clean, defid=defid)
 
#run below as needed       
 
#fill_raw_text()
#fill_clean_text()