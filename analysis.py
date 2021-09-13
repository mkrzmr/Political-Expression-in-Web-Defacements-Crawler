#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 09:12:41 2020

@author: Michael Kurzmeier
This script runs the automated analysis on the defacement database
"""

import sqlalchemy
from sqlalchemy import text
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import punkt
import matplotlib.pyplot as plt
import json
import pandas as pd
#nltk.download() #if run for the first time, uncomment this to download the NLTK corpus
from tld import get_tld

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 30}

plt.rc('font', **font)

engine = sqlalchemy.create_engine('mysql://michael:t"!tnm2Y]"@127.0.0.1/mydb?charset=utf8', encoding='utf-8') # make sure encodign in DB is binary
db = engine.connect()

sw = stopwords.words('english') #defining stopwords and removing them before plotting 
add_stopwords = ["\r", "\r", "\t", "|", "b", "\r\n", "a", "the", "a", "\\n", "to",\
                 "i", "0", "1", "2", "the", "'s", "I", "he", "de", "94" "r", "tha",\
                 "font", "ffffff", "al", "br", "comwww", "la", "var", "x", "burshido"\
                 "color", "star", "ø", "ù", "rgba", "ùšù", 'scrollbar', 'url', 'e', 'p', 'pos', 'put', 'color', 'document']
for w in add_stopwords:
    if w.lower() not in sw:
        sw.append(w)


def write_token(stopwords): #writes the top 100 words per defacement to the db
    sql = ('SELECT DefacementId, clean_text FROM mydb.raw_text;')
    for row in db.execute(sql):
        defid = row[0]
        clean_text=str(row[1])
        token = nltk.word_tokenize(clean_text) #Simple tokenization
        token2 = list(filter(lambda token : punkt.PunktToken(token).is_non_punct,token)) #Remove punctuation 
        token3 = [word.lower() for word in token2] #all lowercase
        token4 = [word for word in token3 if word not in stopwords] #filter out stopwords
        clean_token = token4
        #print(clean_token) #testing
        freq = nltk.FreqDist(clean_token)
        y = json.dumps(freq.most_common(100)) #convert the tokens into a Json array and send them back to the database      
        #print(freq.most_common(100))
        #plt.figure(figsize=(20, 8)) #use this to change plot size
        #freq.plot(20, cumulative=False) # nice for preview, probably better to save all data to file
        #Write back to DB
        sql = text('INSERT INTO `mydb`.`analysis` (DefacementId, token) VALUES (:B, :A);')
        db.execute(sql, A=y, B=defid)
    db.close()

def frequency(stopwords): #runs frequengency analysis on the whole corpus
    sql = ('SELECT DefacementId, clean_text FROM mydb.raw_text;') #bug in SQLalchemy, if you request only one column, strings are truncated
    corpus = []
    for row in db.execute(sql):
        corpus.append(row[1])
        #print(row)
    clean_text=str(corpus)
    token = nltk.word_tokenize(clean_text) #Simple tokenization
    token2 = list(filter(lambda token : punkt.PunktToken(token).is_non_punct,token)) #Remove punctuation 
    token3 = [word.lower() for word in token2] #all lowercase
    token4 = [word for word in token3 if word not in stopwords] #filter out stopwords
    clean_token = token4
    freq = nltk.FreqDist(clean_token)
    plt.figure(figsize=(20, 8))#use this to change plot size
    freq.plot(20, cumulative=False) #plot a graph # better to take output and visualize elsewhere
    for i in freq.most_common(100):
        print (i)
    
    
def bigrams(stopwords): #runs bigram analysis on the whole corpus
    sql = ('SELECT DefacementId, clean_text FROM mydb.raw_text;') #bug in SQLalchemy, if you request only one column, strings are truncated
    corpus = []
    for row in db.execute(sql):
        corpus.append(row[1])
        #print(row)
    clean_text=str(corpus)
    token = nltk.word_tokenize(clean_text) #Simple tokenization
    token2 = list(filter(lambda token : punkt.PunktToken(token).is_non_punct,token)) #Remove punctuation 
    token3 = [word.lower() for word in token2] #all lowercase
    token4 = [word for word in token3 if word not in stopwords] #filter out stopwords
    clean_token = token4
    bigrams = list(nltk.bigrams(clean_token))
    freq_bi = nltk.FreqDist(bigrams)
    frame = pd.DataFrame({'bigrams':freq_bi}) #convert the list into a dataframe
    #print(frame.head(100)) #testing
    frame.to_csv('bigrams.csv', index=True, header=True)
    freq_bi.most_common(20)
    for i in freq_bi.most_common(20):
        print(i[0], i[1])
    plt.figure(figsize=(20, 8))#use this to change plot size
    freq_bi.plot(20)
    
    
def distribution_time():#Defacements over time
    sql = ('SELECT Date FROM `mydb`.`extracted_data`;')
    timestamps = []
    for row in db.execute(sql):
        timestamps.append(row[0]) 
    data = pd.DataFrame(timestamps, columns=['datetime']) #creates the dataframe
    data['count'] = 1 #adds a column
    data['Date'] = pd.to_datetime(data['datetime']) #converts dates to datetime objects
    data = data.set_index('datetime') # index changed
    data.drop(['Date'], axis=1, inplace=True) #original imported timestamps dropped
    result = data.groupby([(data.index.year),(data.index.month)]).sum() #group data by year and month
    result.plot(kind='bar', figsize=(20,20)) #plot graph, can be saved too
    plt.xlabel('Date') #xlabel
    plt.ylabel('Hacktivist Defacements') #ylabel
    plt.show()
    #print(result.head(100))
    result.to_csv('distribution_time.csv', index = True) 
    
    
def defacers_time():#Defacers over time
    sql = ('SELECT Date, Notifier FROM `mydb`.`extracted_data`;')
    timestamps = []
    for row in db.execute(sql):
        timestamps.append(row) 
    data = pd.DataFrame(timestamps, columns=['datetime', 'Notifier'])#create Dataframe
    data['Date'] = pd.to_datetime(data['datetime'])
    data.drop(['datetime'], axis=1, inplace=True) 
    data = data.set_index('Date') #index changed
    result = data.groupby([(data.index.year), (data.index.month), 'Notifier']).size().nlargest(20).unstack() #group data by year and month #UNSTACK!!!! #nlargest needed to macke the graph more readable, stack and unstack to get individual/overall numbers.
    result.sort_index().plot(kind = 'bar', figsize=(20,20), stacked = True, colormap = 'nipy_spectral') #sort the index again before plotting
    #result.sort_index().plot(kind = 'hist',subplots=True, layout = (4,3))
    print(result)
    result.to_csv('defacer_time.csv', index = True) 

def pretty_plot_top_n(series, top_n=3, index_level=0): #aux function for words_time
    r = series\
    .groupby(level=index_level)\
    .nlargest(top_n)\
    .unstack()\
    .reset_index(level=index_level, drop=True)
    r.plot.barh(figsize=(100,100), linewidth=5, alpha=1, stacked = False, table=True) #change graph type and size here, can also export
    #print(r) #testing
    r.to_csv('words_time.csv', index = True) 
    return r.to_frame() #return the top 10 per index
  
def words_time(stopwords):#Words over time as described by https://sigdelta.com/blog/text-analysis-in-pandas/
    sql = ('SELECT `Date`, `raw_text`.`clean_text` FROM `mydb`.`extracted_data` inner join raw_text on extracted_data.DefacementID=`raw_text`.`DefacementId`;;') #use join to select text and DefacementId
    d = list()
    for row in db.execute(sql):
        d.append(pd.DataFrame({'timestamp': row[0], 'text': row[1]},index=[0])) #each defacement text to dataframe
    doc = pd.concat(d) #combines all dataframes
    
    doc['words'] = doc.text.str.strip().str.split('[\W_]+') # now each word becomes its own field
    
    rows = list() #expanding so each word becomes its own row
    for row in doc[['timestamp', 'words']].iterrows():
        r = row[1]
        for word in r.words: #remove all stopwords
            if word.lower() not in stopwords:
                rows.append((r.timestamp, word))

    words = pd.DataFrame(rows, columns=['timestamp', 'word'])
    words = words[words.word.str.len() > 0] #sort out empty strings
    words['word'] = words.word.str.lower() #all lowercase
    words['Date'] = pd.to_datetime(words['timestamp']) #convert time datetimeobject to timestamp
    words = words.set_index('Date') #index changed
    words.drop(['timestamp'], axis=1, inplace=True) #drop old timestamp
    #words.head() testing
    #counts = words.groupby([(words.index.year), (words.index.month)])\ #sorting
    counts = words.groupby([words.index.year])\
    .word.value_counts()\
    .to_frame()\
    .rename(columns={'word':'n_w'})#group by most used words per month and day
    
    word_sum = counts.groupby(level=0)\
    .sum()\
    .rename(columns={'n_w': 'n_d'})
    
    tf = counts.join(word_sum)
    tf['tf'] = tf.n_w/tf.n_d
    pretty_plot_top_n(tf['tf'])
    
#OS breakdown
    
def os_total():
    sql = ('SELECT OS FROM extracted_data') #retrieve the Systems column from the db
    os = []
    for row in db.execute(sql):
        os.append(row[0]) # error if no specific field is referenced, even in a single query
    data = pd.DataFrame({'os':os}) #convert the list into a dataframe
    #print(data.head())
    result = data.groupby('os').size()
    #print(result.head())
    result.plot(kind = 'bar', figsize=(20,20), linewidth=5, alpha=1, stacked = False, table = False) # Tables are badly formatted, better to just get the data and attach in Office
    plt.xlabel('Target Operating System') #xlabel
    plt.ylabel('Total') #ylabel
    plt.show()
    print(result)
    result.to_csv('os_total.csv', index = True) 
    
    #ServerType breakdown
    
def server_total():
    sql = ('SELECT ServerType FROM extracted_data') #retrieve the Systems column from the db
    st = []
    for row in db.execute(sql):
        st.append(row[0]) # error if no specific field is referenced, even in a single query
    data = pd.DataFrame({'ServerType':st}) #convert the list into a dataframe
    #print(data.head()) #testing
    result = data.groupby('ServerType').size()
    result.plot(kind = 'bar', figsize=(20,20), linewidth=5, alpha=1, stacked = False, table = False)
    plt.xlabel('Server Type') #xlabel
    plt.ylabel('Total') #ylabel
    plt.show()
    print(result)
    result.to_csv('server_total.csv', index = True) 
    
    
    #country breakdown

def country_total():
    sql = ('SELECT Country FROM extracted_data') #retrieve the Systems column from the db
    country = []
    for row in db.execute(sql):
        country.append(row[0]) # error if no specific field is referenced, even in a single query
    data = pd.DataFrame({'Country':country}) #convert the list into a dataframe
    #print(data.head()) #testing
    result = data.groupby('Country').size()
    result.plot(kind = 'bar', figsize=(50,50), linewidth=5, alpha=1, stacked = False, table = False)
    plt.xlabel('Country') #xlabel
    plt.ylabel('Total') #ylabel
    plt.show()
    result.to_csv('country_total.csv', index = True) 
    #print('\nCSV String:\n', result) 

def domains_total():
    sql = ('SELECT Domain FROM extracted_data') #retrieve the Domain column from the db
    domain = []
    tld = []
    for row in db.execute(sql):
        domain.append(row[0])
    for i in domain:
        i = get_tld(i, fail_silently=True, fix_protocol=True) #extracting tlds
        tld.append(i)
    data = pd.DataFrame({'Domain':tld})
    #print(data.head()) #testing
    result = data.groupby('Domain').size()
    result.plot(kind = 'bar', figsize=(50,30), linewidth=10, alpha=1, stacked = False, table = False)
    plt.xlabel('TLD') #xlabel
    plt.ylabel('Total') #ylabel
    result.to_csv('tld_total.csv', index = True) 
    plt.show()

#run below as needed

#write_token(sw)
#bigrams(sw)
#frequency(sw)
#distribution_time()
#defacers_time()
#words_time(sw)
#os_total()
#server_total()
#country_total()
#domains_total()