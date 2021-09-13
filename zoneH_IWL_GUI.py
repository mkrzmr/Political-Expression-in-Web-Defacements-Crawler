#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 26 14:10:38 2018

@author: Michael Kurzmeier

WARNING : This must be run with NoScript enabled. 
"""
# This script crawls the Zone-H special archive. It starts at a given Id and attempts to crawl a given number of pages. It writes a set of metadata to 
# a file and saves each page as a screenshot and html file. It expects the following files
# to be present in the working directory:
#     output_list.csv (use the supplied file, add a dummy entry to start from any desired defacementID)
#     error_log_inverse.csv (can be empty, will be filled as error occur)
    
# It also needs:
#     A Firefox installation for selenium to use for browsing - see the profile and extension path below (line 51&52)
#     NoScript extension for Firefox - see extension Id below (line 55)
    
# Module import
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import UnexpectedAlertPresentException
import urllib.request
 
from random import randint

import tkinter as tk
#import tkinter.scrolledtext as st 

#time.sleep(5)
#browser.quit()

#n = input("Please enter start page id: ") #go upwards
ol = open("output_list.csv", "r") #continues on where it left off
for line in ol:
    pass
last = line.strip().split(',') # splits line into list
n= int(last[7]) 
#print("Going up from page id " +last[7] +'. This crawler may increment by 100.')



output = open('output_list.csv', 'a')
error = open ('error_log_inverse.csv', 'a')

extension_dir = "/home/michael/.mozilla/firefox/voibkjeo.selenium/extensions/" #adjust as needed
fp = webdriver.FirefoxProfile('/home/michael/.mozilla/firefox/voibkjeo.selenium/') #adjust as needed
browser = webdriver.Firefox(fp)
extensions = [
    '{73a6fe31-595d-460b-a920-fcc0f8843232}.xpi', #this is the NosCript extension, adjust as needed
    ]
 
for extension in extensions:
    browser.install_addon(extension_dir + extension, temporary=True) #extensions are enabled


def process_page(n): #main loop
    
    skip = False
    url = ("http://zone-h.com/mirror/id/"+str(n))
    
    try:
        browser.get(url)
        browser.maximize_window()
    except UnexpectedAlertPresentException: #handles popups
        pass
        
    # Wait 10 seconds for page to load //*[@id="propdeface"]/iframe
    timeout = 5

    try:
        # Wait until the frame is loaded.
        WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//iframe")))        
    except TimeoutException:
        e = ('\n'+str(n)+', timeout')
        error.write(e) #writes error log
        print(e)
        text_area.insert(tk.END, e)
    except UnexpectedAlertPresentException: #handles popups
        pass
    
    try:
        browser.find_element_by_xpath ("//*[@id='error']/p/img") # gives better error logs
        e = '\n'+(str(n)+ ', Invalid')
        print(e)
        text_area.insert(tk.END, e)
    except NoSuchElementException:
        pass

    
    try: #Selenium attempts to find all metadata the is on the page
        date = browser.find_element_by_xpath("//*[@id='propdeface']/ul/li[1]")  
        notifyer = browser.find_element_by_xpath("//*[@id='propdeface']/ul/li[2]/ul/li[1]")
        domain = browser.find_element_by_xpath("//*[@id='propdeface']/ul/li[2]/ul/li[2]")
        ip = browser.find_element_by_xpath("//*[@id='propdeface']/ul/li[2]/ul/li[3]")
        system = browser.find_element_by_xpath("//*[@id='propdeface']/ul/li[3]/ul/li[1]")
        server = browser.find_element_by_xpath("//*[@id='propdeface']/ul/li[3]/ul/li[2]")
        data = [date, notifyer, domain, ip, system, server]
    
    #titles_element = browser.find_elements_by_xpath("//*[@id='propdeface']/ul") #this should find elements individually and write to a list

        data_text = [x.text for x in data]
        try: #ip and country flag not present in all mirrors
            country = browser.find_element_by_xpath("//*[@id='propdeface']/ul/li[2]/ul/li[3]/img")  
            img = country.get_attribute("alt")
            data_text.append (img) #alt text from counrty flag
        except NoSuchElementException:
            img = "no ip"
            data_text.append(img)
        
        data_text.append (str(n))
        data_text.append (url)
        #print (data_text) #testing
        x = (str(','.join(data_text)+'\n'))
        output.write(x)
        print(x)
        x = ('\n' + x) #add newline for gui
        text_area.insert(tk.END, x)
    except NoSuchElementException:
        e = ('\n'+str(n)+', page did not load')
        error.write(e) #writes error log
        print (e)
        text_area.insert(tk.END, e)
    except UnexpectedAlertPresentException: #handles popups
        pass
        
    
    try: 
        iframe_url = browser.find_element_by_xpath("//*[@id='propdeface']/iframe") #open iframe and takes full page screenshot
        iframe = iframe_url.get_attribute("src")
        browser.get(iframe)
        browser.save_screenshot('screenshot_'+str(n)+'.png') #takes a screenshot
        urllib.request.urlretrieve(iframe, str(n)+'.txt') #saves the page as .txt
    except NoSuchElementException:
        e = ('\n'+str(n)+', iframe did not load')
        error.write(e) #writes error log
        print(e)
        text_area.insert(tk.END, e)
        skip = True
        
    except UnexpectedAlertPresentException: #handles popups
        pass

    data =[]
    return skip

def scrape (n):

    #target = input("Please enter the number of pages you want to attempt: ") #Defines the number of pages to be TRIED
    target = entry.get()
    target = int(target)
    #data = []
    skip_count = 0
    #message = tk.StringVar() #left off here, update more often
    #message.trace("w", update)
    while (target > 0): #now counting attempts instead of captures
        message = ('\n############ Attempting pageId '+ str(n) +'. '+str(target) +' attempts left in queue. ############')
        print(message)
        text_area.insert(tk.END, message)
        update()
        skip = process_page(n)
        target -=1
        if skip == True and skip_count <  4 : #to avoid being stuck in large arrays of invalid Ids, the crawler skips ahead if series of invalid pages are detected
                step = randint(1,10)
                n = n+step
                skip_count += 1
                message = ('\nSkipping up by '+str(step)+', skip_count is '+str(skip_count)+'\n')
                print(message)
                text_area.insert(tk.END, message)
                update()
        elif skip == True and skip_count > 3:
                step = randint(10,100)
                n = n+step
                skip_count += 1
                message = ('\nSkipping up by '+str(step)+', skip_count is '+str(skip_count)+'\n')
                print(message)
                text_area.insert(tk.END, message)
                update()
        else: 
            n+=1
            skip_count = 0
    message = ("\n *******************Queue completed*******************")
    text_area.insert(tk.END, message)
    update()
   
def update(*args):
    root.update()
    text_area.see(tk.END)


### gui layout ###
            
root = tk.Tk()

heading = tk.Label(text = "Zone-H Special Archive Crawler")
heading.pack()

leftoff = tk.Label(text = "Going up from page id " +last[7] +'. This crawler may increment by 100.')
leftoff.pack()

howmany = tk.Label(text = "Please enter the number of pages you want to attempt: ")
howmany.pack()

entry = tk.Entry()
entry.insert(0, "300")
entry.pack()

text_area = tk.Text(root, 
                            width = 100,  
                            height = 50)
#text_area.configure(state ='normal')  
text_area.pack()  
#text_area.grid(column = 0, pady = 10, padx = 10) 

buttonStart = tk.Button(
    text="Start crawl",
    width=25,
    height=5,
    command = lambda: scrape(n)
)
buttonStart.pack()

buttonEnd = tk.Button(
        text = "Quit",
        width = 25,
        height = 5,
        command = lambda: root.destroy())
buttonEnd.pack()

root.mainloop()
### end gui layout ###

    
#scrape(n)    
browser.quit()
output.close()
error.close()