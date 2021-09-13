#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 10:26:48 2020

@author: Michael Kurzmeier
"""

#select all in scope defacements and place them in a folder

import shutil

data = open('List_InScope.csv')
headers = data.readline() #reading the first line


for line in data: #find all in scope entries
    l = line.strip().split('@')
    if len(l[9]) > 0:
        text = ('pages/'+l[7]+'.txt')
        screen = ('screens/screenshot_'+l[7]+'.png')
        shutil.copy(text, '/home/michael/Desktop/Dataset - Copy CS2/cs2/pages')
        shutil.copy(screen, '/home/michael/Desktop/Dataset - Copy CS2/cs2/screens/') 
        print('Copied DefacementId ' +l[7])