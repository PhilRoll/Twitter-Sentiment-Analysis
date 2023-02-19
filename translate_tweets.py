import sys
import os
import time
import tweepy
import pandas as pd
import nltk
import numpy as np
from deep_translator import GoogleTranslator
import re
import emoji

def clean_tweet(text):
    text = re.sub(r'http\S+','',text, flags=re.M)   #Rimozione degli URLs
    text = re.sub(r"&amp",'',text)                  #Rimozione "&amp"
    text = re.sub(r'@[a-zA-Z0-9_]+', '', text)      #Rimozione dei tags @users
    text = emoji.demojize(text, language='en')      #Converte le emoji in testo
    text = re.sub(r'[^a-zA-ZÀ-ÿ\.!?;#]', ' ', text) #rimozione di tutto eccetto caratteri . ! ? ; ed #
    text = re.sub(';','. ', text)             #converte i ; in .
    text = re.sub(r'(\.+ *)+','. ',text)      #piu punti consecutivi in uno
    text = re.sub(r'(\!+ *)+','! ',text)      #piu punti esclamativi consecutivi in uno
    text = re.sub(r'(\?+ *)+','? ',text)      #piu punti esclamativi consecutivi in uno 
    text = re.sub(r'\s\s+',' ', text)        #Rimozione spazi/tab/ecc
    text = re.sub(r'^(\.+ *)+','',text)      #rimozione punti a inizio frase  
    text = re.sub(r'(\.+ *)+$','',text)      #rimozione punti a fine frase    
    return text


def translate_to_english(text):
    return GoogleTranslator(source='auto', target='en').translate(text)

#caricamento del dataframe
df = pd.read_csv('dataframes/tweets.csv')

df.drop_duplicates(subset='Tweet', keep = 'first', inplace = True)  #Rimozione dei tweet duplicati
df = df[~df['Tweet'].str.startswith("df")]                          #Rimozione dei re-tweets residui  

#divide il dataframe in tweets inglesi e tweets in altre lingue
df1 = df.loc[df.lang.str.contains('en')]
df2 = df.loc[~df.lang.str.contains('en')]
df2 = df2.reset_index(drop=True) 
print("("+str(len(df2))+"tweets)")

#traduzione dei tweets clean_tweet(text)
df2['Tweet'] = df2['Tweet'].apply(lambda x: clean_tweet(x))
df2 = df2[~(df2["Tweet"] =="")]  
df2['Tweet'] = df2['Tweet'].apply(lambda x: translate_to_english(x))

#merge dei due dataframe
df = pd.concat([df1, df2], ignore_index=True)
#elimina colonna lingua (superflua)
df = df.drop(columns=['lang'])

df.to_csv("dataframes/tweets_translated.csv", mode='a', index=False) #salvare il dataframe in un CSV (MODALITA APPEND)