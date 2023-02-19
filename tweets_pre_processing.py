import csv
import re
import string
import contractions
from nltk import pos_tag
import demoji
import emoji
import matplotlib.pyplot as plt
import nltk
import numpy as np
import pandas as pd
import preprocessor as p
import sklearn
import tweepy
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import wordninja 
from IPython.display import display
from brand_lists import *
#nltk.download('omw-1.4') #nltk.download('stopwords')

def get_users_list_from_df(df):
    all_user_list = df["User"].astype('string').tolist() #lista di utenti
    return list(np.unique(all_user_list))

#Funzione di pulizia dei tweet: rimuove URLs, handler degli utenti (@user), punteggiatura ecc ecc.
def clean_tweet(text):
    text = re.sub(r'http\S+','',text, flags=re.M)   #Rimozione degli URLs
    text = re.sub(r"&amp",'',text)
    text = re.sub(r'@[a-zA-Z0-9_]+', '', text)      #Rimozione dei tags @users
    text = emoji.demojize(text, language='en')      #Converte le emoji in testo
    text = contractions.fix(text.lower())           #Rimuove le forme contratte dal testo (es: i'm -> i am) 
    text = re.sub(r'[^a-zA-ZÀ-ÿ\.!?;#]', ' ', text)  #rimozione di tutto eccetto caratteri . ! ? ; ed #
    text = re.sub(';','. ', text)             #converte i ; in .
    text = re.sub(r'(\.+ *)+','. ',text)      #piu punti consecutivi in uno
    text = re.sub(r'(\!+ *)+','! ',text)      #piu punti esclamativi consecutivi in uno
    text = re.sub(r'(\?+ *)+','? ',text)      #piu punti esclamativi consecutivi in uno 
    text = re.sub(r'\s\s+',' ', text)        #Rimozione spazi/tab/ecc
    text = re.sub(r'^(\.+ *)+','',text)      #rimozione punti a inizio frase  
    text = re.sub(r'(\.+ *)+$','',text)      #rimozione punti a fine frase    
    #text = ' '.join(dict.fromkeys(text.split()))   #Rimuove parole duplicate
    return text


#separa gli hashtag formati da piu parole e le sostituisce nel testo
def split_hashtag(text):
    hashtag_list = re.findall('#\w+', text)         #estrae gli hashtag
    for h in hashtag_list:
        text = re.sub(h, ' '.join(wordninja.split(h)),text) 
    return re.sub('#','', text)


#tokenizza il testo
def tokenize_text(text):
    words_tokenizer = nltk.tokenize.WhitespaceTokenizer()
    return words_tokenizer.tokenize(text)


#Funzione di rimozione delle stopwords
english_stopword = stopwords.words('english')
def remove_stopwords(text):
    return str.join(" ",[word for word in text.split() if word not in english_stopword])


#Per applicare al meglio la lemmatizzazione bisogna sapere il tipo di parola su cui sta operando --> [Part of Speech (PoS)]
##Funzione che associa alla parola il suo tipo (verbo, nome, aggettivo, avverbio). 
def map_postag_into_wordnet(pos_tag):
    #Creazione del dizionario:
    words_map = {"j": wordnet.ADJ, 
                "n": wordnet.NOUN,
                "v": wordnet.VERB,
                "r": wordnet.ADV}
    default_pos = wordnet.NOUN                                      #opzione di fefault in caso di fallimento del mapping:
    wordnet_tag = words_map.get(pos_tag[0].lower(), default_pos)    #restituisce il valore associato alla chiave passata come argomento
    return wordnet_tag


#Funzione di lemmatizzazione delle parole
lemmatizer = WordNetLemmatizer()
def lemmatize_text(text):
    tagged_word_list = pos_tag(tokenize_text(text))  
    lemma_list = []
    for word, tag in tagged_word_list: 
        wrdnt_tag = map_postag_into_wordnet(tag)
        lemma = lemmatizer.lemmatize(word, pos=wrdnt_tag)
        lemma_list.append(lemma)
    return ' '.join(lemma_list)




#APPLICAZIONE DEL PRE-PROCESSING

#Caricamento database da file CSV

twitter_dataframe = pd.read_csv('dataframes/tweets_translated.csv')

all_user_list = get_users_list_from_df(twitter_dataframe) #lista di utenti
print("loading CSV: "+str(twitter_dataframe.shape[0])+" tweet found. (",len(all_user_list)," users found)\n")

#rimozione dei tweet non necessari
print("Removing NaN rows, duplicates and RE-Tweets")
twitter_dataframe.dropna(inplace= True)
twitter_dataframe.drop_duplicates(subset='Tweet', keep = 'first', inplace = True)           #Rimozione dei tweet duplicati
twitter_dataframe = twitter_dataframe[~twitter_dataframe['Tweet'].str.startswith("RT")]     #Rimozione dei re-tweets residui   

print("Replacing synonyms and removing tweets that do not contian tags")
twitter_dataframe['Tweet'] = np.vectorize(replace_all_synonyms)(twitter_dataframe['Tweet']) #Sostituzione dei sinonimi
twitter_dataframe = twitter_dataframe[twitter_dataframe["Tweet"].str.contains('\\b(?:'+'|'.join(all_brands_tags)+')\\b' ,flags=re.IGNORECASE)] #Rimozione dei tweets che non contengono i tags

print("Cleaning tweets:\n[Removing -> URLs, @Handler, punctuations, end-of-line/tab]\n[Converting -> emoji, contracted forms]")
twitter_dataframe['Cleaned-tweet'] = np.vectorize(clean_tweet)(twitter_dataframe['Tweet'])  #Creazione della colonna dei tweet pre-processati, utilizzando la funzione "clean_tweet"
twitter_dataframe = twitter_dataframe[~(twitter_dataframe["Cleaned-tweet"] =="")]           #Rimozione dei tweet rimasti vuoti
#twitter_dataframe['Cleaned-tweet'] = twitter_dataframe['Cleaned-tweet'].apply(lambda x: ' '.join([word for word in x.split() if len(word)>2])) #Rimozione delle parole corte (1-2 lettere) <--Metodo poco utile?

print("Applying split-hashtag:")
twitter_dataframe['Cleaned-tweet'] = np.vectorize(split_hashtag)(twitter_dataframe['Cleaned-tweet'])  

print("Applying lemmatization:")
twitter_dataframe['Cleaned-tweet'] = np.vectorize(lemmatize_text)(twitter_dataframe['Cleaned-tweet'])  
#twitter_dataframe['Cleaned-tweet'] = twitter_dataframe['Cleaned-tweet'].apply(remove_stopwords) 

twitter_dataframe = twitter_dataframe.sort_values(by='User')    #Riordina i tweet in base agli utenti
twitter_dataframe = twitter_dataframe.reset_index(drop=True)    #Reset degli index del dataframe

all_user_list = get_users_list_from_df(twitter_dataframe) #lista di utenti
print("Preprocessing complete, "+str(twitter_dataframe.shape[0])+"tweets remained. (",len(all_user_list)," users)\nSaving preprocessed tweets...")
twitter_dataframe.to_csv("dataframes/pre_processed_tweets.csv", index=False) 
print("Done!")
