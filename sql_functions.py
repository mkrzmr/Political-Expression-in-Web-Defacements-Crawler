#!/usr/bin/env python3
# -*- coding: ISO-8859-1 -*-
"""
Created on Wed Mar  4 16:16:07 2020
# connecting to local mysql database and cleaning the imported_data, copy over to extraced_data
@author: Michael Kurzmeier
"""

import glob2
import sqlalchemy
from sqlalchemy import text
from bs4 import BeautifulSoup

filenames = glob2.glob('*.txt')

engine = sqlalchemy.create_engine('mysql://michael:{password}]"@127.0.0.1/mydb?charset=utf8', encoding='ISO-8859-1') # make sure encoding in db matches(utf8mb4))
db = engine.connect()

def fill_raw_text(): #loads all text files and inserts them into database
    for i in filenames:
        with open(i, 'rb') as infile:
            html = infile.read()
            defid = i[:-4]
            sql = text('INSERT INTO `mydb`.`raw_text` (`DefacementId`, `raw_html`) VALUES (:defid, :msg)')
            db.execute(sql, defid=defid, msg=html)
    db.close()
    
def fill_clean_text(): #loads all raw_html fields, strips away html tags and writes output to clean_text
    sql = ('SELECT DefacementId, raw_html FROM mydb.raw_text;')
    for row in db.execute(sql):
        print(row)
        defid = row[0]
        raw_html=row[1]#.decode('ISO-8859-1', errors = 'ignore') # 
        soup = BeautifulSoup(raw_html,"html5lib")
        clean = soup.get_text(strip=True) #strip away html tags
        #clean =clean.encode() #encode to binary again
        sql = text ('UPDATE `mydb`.`raw_text` SET `clean_text` = :clean WHERE (`DefacementId` = :defid);')
        db.execute(sql, clean=clean, defid=defid)
    db.close()
     
def process_date(): #removes the "Mirror saved on:" part of the date field so it can be read as a timestamp 
    sql = ('SELECT DefacementId, Date FROM mydb.imported_data;')
    for row in db.execute(sql):
        defid = row[0]
        newdate = row[1]
        newdate = newdate[17:]
        print (newdate)
        sql = text('UPDATE `mydb`.`extracted_data` SET `Date` = :newdate WHERE (`DefacementId` = :defid);' )
        db.execute(sql, newdate=newdate, defid = defid)
    db.close()
    
def process_domain(): #Removes 'Domain: 'from the Domain field for analysis
    sql = ('SELECT DefacementId, Domain FROM mydb.imported_data;')
    for row in db.execute(sql):
        defid = row[0]
        newdomain = row[1]
        newdomain = newdomain[8:]
        print(newdomain)
        sql = text('UPDATE `mydb`.`extracted_data` SET `Domain` = :newdomain WHERE (`DefacementId` = :defid);' )
        db.execute(sql, newdomain=newdomain, defid = defid)
    db.close()
    
def process_ip(): #Removes 'IP Address: ' from the IP field, replaces it with 'No Ip' if none present
    sql = ('SELECT DefacementId, IP FROM mydb.imported_data;')
    for row in db.execute(sql):
        defid = row[0]
        newip = row[1]
        newip = newip[12:]
        if len(newip) < 1:
            newip = 'No Ip'
        print(newip)
        sql = text('UPDATE `mydb`.`extracted_data` SET `IP` = :newip WHERE (`DefacementId` = :defid);' )
        db.execute (sql, newip = newip, defid = defid)
    db.close()
    
def process_os(): #Removes 'System: ' from the OS cloumn
    sql = ('SELECT DefacementId, OS FROM mydb.imported_data;')
    for row in db.execute(sql):
        defid = row[0]
        newos = row[1]
        newos = newos[8:]
        print(newos)
        sql = text('UPDATE `mydb`.`extracted_data` SET `OS` = :newos WHERE (`DefacementId` = :defid);' )
        db.execute (sql, newos=newos, defid=defid)
    db.close()
    
def process_server(): #Removes 'Web server: ' from ServerType, replaces with "not specified" if none present
    sql = ('SELECT DefacementId, ServerType FROM mydb.imported_data;')
    for row in db.execute(sql):
        defid = row[0]
        newserver = row[1]
        newserver = newserver[12:] #check
        if len(newserver) < 1:
            newserver = 'Server type not specified'
        print(newserver)
        sql = text('UPDATE `mydb`.`extracted_data` SET `ServerType` = :newserver WHERE (`DefacementId` = :defid);' )
        db.execute (sql, newserver=newserver, defid=defid)
    db.close()
    
def process_country(): #Replace 'No Ip' with 'No country flag'
    sql = ('SELECT DefacementId, Country FROM mydb.imported_data;')
    for row in db.execute(sql):
        defid = row[0]
        country = row[1]
        if country == 'no ip':
            country = 'No country flag'
        print(country)
        sql = text('UPDATE `mydb`.`extracted_data` SET `Country` = :country WHERE (`DefacementId` = :defid);' )
        db.execute (sql, country=country, defid=defid)
    db.close()
    
def process_notifier(): #Removes 'Notifier : '
    sql = ('SELECT DefacementId, Notifier FROM mydb.imported_data;')
    for row in db.execute(sql):
        defid = row[0]
        newNotifier =row[1]
        newNotifier = newNotifier[13:]
        print(newNotifier)
        sql = text('UPDATE `mydb`.`extracted_data` SET `Notifier` = :newNotifier WHERE (`DefacementId` = :defid);' )
        db.execute (sql, newNotifier=newNotifier, defid=defid)
    db.close()
    
#run the below as needed

#fill_raw_text()
#fill_clean_text()
#process_date()
#process_domain()
#process_ip()
#process_os()
#process_server()
#process_country()
#process_notifier()
