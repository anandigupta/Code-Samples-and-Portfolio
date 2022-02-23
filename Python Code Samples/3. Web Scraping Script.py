#!/usr/bin/env python
# coding: utf-8

# # Anandi Gupta
# # Problem Set 3
# 
# ## Task 1
# 
# ### Question 1
# 

# In[120]:


import pandas as pd
import numpy as np
import time
import random
import sqlite3
import copy


# In[2]:


url = "https://investmentpolicy.unctad.org/international-investment-agreements/by-economy"

#use pandas to read in tables from webpage
country_data = pd.read_html(url)


# In[3]:


#display data
country_data


# In[4]:


#convert list to df

country_df = pd.concat(country_data, ignore_index = True)


# In[5]:


country_df.head()
country_df.columns


# In[6]:


#clean total bits columns to create necessary variables

country_df['n_bits'] = country_df['*  TOTAL BITs'].str.split("(").str[0].str.strip()
country_df['n_bits_active_temp'] = country_df['*  TOTAL BITs'].str.split("(").str[1].str.strip()
country_df['n_bits_active'] = country_df['n_bits_active_temp'].str.split(" ").str[0].str.strip()
country_df['n_bits']= country_df['n_bits'].astype('int16')

#check to see what nan values represent
check_for_nan = country_df[country_df['n_bits_active_temp'].isnull()]
print (check_for_nan)

#replaces nas with 0
country_df['n_bits_active']= country_df['n_bits_active'].replace(np.nan, 0)

country_df['n_bits_active']= country_df['n_bits_active'].astype('int16')


# In[7]:


#filter to relevant variables

country_df = country_df[['Name', 'n_bits', 'n_bits_active']]
country_df.head()


# In[8]:


#import list of un countries

url2 = "https://www.un.org/about-us/member-states"

import requests # For downloading the website
from bs4 import BeautifulSoup # For parsing the website

page = requests.get(url2)
page.status_code # 200 == Connection


# In[9]:


#We've downloaded the entire website
page.content


# In[10]:


# Parse the content 
soup = BeautifulSoup(page.content, 'html.parser')

# Let's look at the raw code of the downloaded website
print(soup.prettify())


# In[11]:



soup.find_all('h2') # Here I'm locating all the header level 2 tags

# Cconvert the tag to text
soup.find_all('h2')[1].get_text()

# Using a list comprehension we can do this for each h2 tag
content1 = [i.get_text() for i in soup.find_all(('h2'))]
content1


# In[12]:


#!pip install country_converter


# In[13]:


#use country converter to standardize country names

import country_converter as coco
del content1[0]
standard_names = coco.convert(names=content1, to='name_short')
print(standard_names)


# In[14]:


#delete countries that break country converter, then apply converter to original df

country_df = country_df.loc[country_df["Name"] != "Channel Islands"]
country_df = country_df.loc[country_df["Name"] != "Yugoslavia (former)"]
country_df['Name'] = country_df.Name.apply(lambda x: coco.convert(names=x, to='name_short', not_found= "None"))


# In[77]:


#subset country data to those in list of UN countries

country_level = country_df.loc[country_df['Name'].isin(standard_names)]
country_level


# In[168]:


#Create sql database that doesn't exist yet
conn = sqlite3.connect("ps3_db.sqlite")


# In[ ]:


#Write database to sql
country_level.to_sql("country_level",conn)


# ### Question 2

# In[16]:


page = requests.get(url)
page.status_code # 200 == Connection

# Parse the content 
soup = BeautifulSoup(page.content, 'html.parser')


# Let's look at the raw code of the downloaded website
print(soup.prettify())


# In[17]:


#identify all instances of website links

content2 = [i.attrs.get("href") for i in soup.find_all(('a'))]


# In[18]:


#subset to country specific website links only using text search

substring = "/countries"

substring_in_list = [string for string in content2 if substring in string]


# In[19]:


substring_in_list


# In[20]:


#convert to full working urls

all_urls = ["https://investmentpolicy.unctad.org" + s for s in substring_in_list]
all_urls


# In[21]:


#check for countries with 0 bits as these urls will break the webscraper

country_df_temp = pd.concat(country_data, ignore_index = True)
country_df_temp = country_df_temp.loc[(country_df_temp['*  TOTAL BITs'] == "0")]


# In[23]:


#convert column of countries with 0 bits to list and standardize names to match urls

to_drop = country_df_temp.Name.tolist()

for i in range(len(to_drop)):
    to_drop[i] = to_drop[i].lower()
    to_drop[i] = to_drop[i].replace(" ", "-")
    to_drop[i] = to_drop[i].replace("(", "")
    to_drop[i] = to_drop[i].replace(")", "")
    to_drop[i] = to_drop[i].replace("é", "-")
to_drop


# In[24]:


#loop through urls and find those containing country names with zero bits

matches = []
 
for match in all_urls:
    for dropped in to_drop:
        
        if dropped in match:
            matches.append(match)


# In[25]:


#compile final list of urls having dropped 0 bits countries

final_urls = [x for x in all_urls if x not in matches]
final_urls


# In[26]:


#loop through urls and read in tables

list_of_df = []

for i in range(0, len(final_urls)) :


    x = final_urls[i]
    test = pd.read_html(x)
    test = pd.concat(test, ignore_index = True)
    test = test.loc[test['Type'] == "BITs"]
    test = test[['Short title', 'Type', 'Status', 'Date of signature', 'Date of entry into force', 'Termination date', 'Parties']]
    test['country'] = x.split("/")[-1].title()
    list_of_df.append(test)
    time.sleep(random.uniform(.1,1))


# In[27]:


test.head()


# In[91]:


#convert back to df

df = pd.concat(list_of_df)


# In[92]:


#clean up variables as requested

df['Status'] = df.Status.replace("In force", "active")
df['Status'] = df.Status.replace("Signed (not in force)", "signed")
df['Status'] = df.Status.replace("Terminated", "terminated")
df = df.rename(columns={"country": "country_A", "Parties": "country_B", "Status": "status"})


# In[93]:


#reset index as each table was restarting the index

df = df.reset_index(drop=True)


# In[94]:


#grab the years for the relevant date fields

df['Date of signature']  = df['Date of signature'].str.split("-").str[-1]
df['Date of signature']  = df['Date of signature'].str.split("/").str[-1]
df['Date of signature'] = pd.to_datetime(df["Date of signature"], format='%Y')
df['year_signed'] = pd.DatetimeIndex(df['Date of signature']).year

df['Date of entry into force']  = df['Date of entry into force'].str.split("-").str[-1]
df['Date of entry into force']  = df['Date of entry into force'].str.split("/").str[-1]
df['Date of entry into force'] = pd.to_datetime(df['Date of entry into force'], format='%Y')
df['year_enforced'] = pd.DatetimeIndex(df['Date of entry into force']).year

df['Termination date']  = df['Termination date'].str.split("-").str[-1]
df['Termination date']  = df['Termination date'].str.split("/").str[-1]
df['Termination date'] = pd.to_datetime(df['Termination date'], format='%Y')
df['year_terminated'] = pd.DatetimeIndex(df['Termination date']).year


# In[96]:


#convert years to integers
df['year_signed'] = df['year_signed'].astype('float')
df['year_enforced'] = df['year_enforced'].astype('float')
df['year_terminated'] = df['year_terminated'].astype('float')


# In[97]:


df.head()


# In[98]:


#drop countries that don't appear in the country converter and fix names that break converter

df['country_A'] = df['country_A'].replace("Cabo-Verde", "Cabo Verde")

indexNames = df[ df['country_A'] == "Yugoslavia-Former-" ].index

df.drop(indexNames , inplace=True)


# In[99]:


#apply converter
df['country_A'] = df.country_A.apply(lambda x: coco.convert(names=x, to='name_short', not_found= "None"))


# In[100]:


#same process for country b
indexNames = df[ df['country_B'] == "BLEU (Belgium-Luxembourg Economic Union)" ].index

df.drop(indexNames , inplace=True)

indexNames = df[ df['country_B'] == "Yugoslavia (former)" ].index

df.drop(indexNames , inplace=True)


# In[101]:


df['country_B'] = df.country_B.apply(lambda x: coco.convert(names=x, to='name_short', not_found= "None"))


# In[102]:


df.head()


# In[158]:


#subset to agreements in between un member countries (in standard names list)

final2 = df.loc[(df['country_A'].isin(standard_names)) & (df['country_B'].isin(standard_names)) ]
final2.head()


# In[159]:


#drop irrelevant variables
dyad_level = final2.drop(['Short title', 'Type', 'Date of signature', 'Date of entry into force', 'Termination date'], axis=1)


# In[160]:


dyad_level.head()


# In[169]:


#write table with bits details to sql database
dyad_level.to_sql("dyad_level",conn)

