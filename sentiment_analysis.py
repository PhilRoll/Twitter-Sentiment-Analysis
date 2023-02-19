import os
from textblob import TextBlob
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from flair.models import TextClassifier
from flair.data import Sentence
from afinn import Afinn
from sentistrength import PySentiStr
import pandas as pd
import numpy as np
from nltk import tokenize
MODULE = 'C:/Users/filip/AppData/Local/Programs/Python/Python310/Lib/site-packages/pattern'
import sys 
if MODULE not in sys.path: sys.path.append(MODULE)
from pattern.en import sentiment
from brand_lists import *
import re


#DEFINIZIONE DELLE FUNZIONI PER IL CALCOLO DELLA POLARITA'

#calcolo polarità tramite TextBlob 
def sentiment_textblob(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment[0]
    if polarity > 0: return 1
    elif polarity < 0: return -1
    else: return 0

#calcolo polarità tramite Spacy-TextBlob 
def sentiment_spacytextblob(text):
    nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe('spacytextblob')
    doc = nlp(text)
    polarity = doc._.polarity
    if polarity > 0: return 1
    elif polarity < 0: return -1
    else: return 0

#calcolo polarità tramite Vader 
def sentiment_vader(text):
    analyzer = SentimentIntensityAnalyzer()
    polarity = analyzer.polarity_scores(text)['compound']
    if polarity > 0: return 1
    elif polarity < 0: return -1
    else: return 0

#calcolo verdetto tramite Flair
classifier = TextClassifier.load('en-sentiment')
def sentiment_flair(text):
    sentence = Sentence(text)
    classifier.predict(sentence)
    if "POSITIVE" in str(sentence.labels): return 1
    if "NEGATIVE" in str(sentence.labels): return -1
    if "NEUTRAL" in str(sentence.labels): return 0

#calcolo verdetto tramite AFINN
def sentiment_afinn(text):
    afinn = Afinn()
    polarity = afinn.score(text)  
    if polarity > 0: return 1
    elif polarity < 0: return -1
    else: return 0

"""#calcolo verdetto tramite PATTERN
def sentiment_pattern(text):
    polarity = sentiment(text)[0]
    if polarity > 0: return 1
    elif polarity < 0: return -1
    else: return 0"""

#calcolo verdetto tramite SentiStrength
def sentiment_sentistrength(text):
    senti = PySentiStr()
    senti.setSentiStrengthPath('C:/SentiStrengthData/SentiStrength.jar') # Note: Provide absolute path instead of relative path
    senti.setSentiStrengthLanguageFolderPath('C:/SentiStrengthData/') # Note: Provide absolute path instead of relative path
    polarity = senti.getSentiment(text)[0]
    if polarity > 0: return 1
    elif polarity < 0: return -1
    else: return 0

#funzione di media
def average_to_sentiment(val):
    if val >=0.5: return 1
    if val <=-0.5: return -1
    else: return 0

def get_most_rated(pos,neg,neu):
    if pos > neg and pos > neu: return 1
    elif neg > pos and neg > neu: return -1
    else: return 0

#RISULTATO FINALE (si sceglie per maggioranza)
def all_libraries_sentiment(text):
    pos = 0
    neg = 0
    neu = 0
    results = []
    results.append(sentiment_textblob(text))
    results.append(sentiment_spacytextblob(text))
    results.append(sentiment_vader(text))
    results.append(sentiment_flair(text))
    results.append(sentiment_afinn(text))
    results.append(sentiment_sentistrength(text))
    for val in results:
        if val > 0: pos += 1
        elif val < 0: neg += 1
        else: neu += 1
    return get_most_rated(pos,neg,neu)


#stampa dei risultati
def print_result(val):
    if val == 1: return "POSITIVE"
    elif val == -1: return "NEGATIVE"
    else: return "NEUTRAL"


#funzione che calcola il sentiment in base alla libreria selezionata
def get_sentiment_from_lib(library, text):
    if library == "textblob":
        return sentiment_textblob(text)
    if library == "spacytextblob":
        return sentiment_spacytextblob(text)
    if library == "vader":
        return sentiment_vader(text)
    if library == "flair":
        return sentiment_flair(text)
    if library == "afinn":
        return sentiment_afinn(text)
    if library == "sentistrength":
        return sentiment_sentistrength(text)
    if library == "ALL":
        return all_libraries_sentiment(text)
    


#
# FASE DI SENTIMENT DEI TWEETS (SCELTA DI VADER COME LIBRERIA)
#


library = "vader"

#PRIMO BLOCCO -> CREAZIONE TABELLA USERS-TAGS
#dichiarazione dei dati
twitter_dataframe = pd.read_csv('dataframes/pre_processed_tweets.csv',encoding='utf8')
twitter_dataframe = twitter_dataframe.dropna() 
all_user_list = list(np.unique(twitter_dataframe["User"])) #lista di utenti #lista di utenti


#Creazione della tabella preliminare [User - tags]
user_sentiment_dataframe = pd.DataFrame(all_user_list, columns=['User'])    #creazione del dataframe
for tag in all_brands_tags:
    user_sentiment_dataframe[tag] = 0      
#creazione della tabella delle frasi (tweets scomposti)
sentences_dataframe = pd.DataFrame(columns=['User','Sentence','Sentiment']) 


#CALCOLO DEI SENTIMENTI PER TUTTI GLI UTENTI    
for user in all_user_list:
    user_dataframe = twitter_dataframe[twitter_dataframe["User"]  == user].drop_duplicates(subset="Cleaned-tweet", keep="first") #estrazione dei tweets del singolo utente (senza duplicati)
    print("\nComputing sentiment for: [",user," - ",user_dataframe.shape[0]," tweets]")
    if not user_dataframe.empty:                                           #se non è vuoto
        tweets_text = '. '.join(user_dataframe['Cleaned-tweet'].values)    #tutti i tweets dell'utente in un unico testo
        sentence_list = tokenize.sent_tokenize(re.sub(r'(\.+ *)+','. ',tweets_text)) #creazione lista "sentence" (frasi/periodi)
        for tag in all_brands_tags:                #per ogni tag
            if tag not in tweets_text: continue    #ottimizzazione per ciclare piu velocemente
            pos = 0
            neg = 0
            neu = 0                                #valore di polarità cumulata
            num_sentence = 0                       #numero di frasi associate ad un tag
            for sentence in sentence_list:
                if tag in sentence:
                    num_sentence += 1
                    sentiment = get_sentiment_from_lib(library,sentence)
                    sentences_dataframe.loc[len(sentences_dataframe)] = [user,sentence,sentiment]
                    if sentiment > 0: pos += 1
                    elif sentiment < 0: neg += 1
                    else: neu += 1 
            if num_sentence!=0:
                user_sentiment_dataframe.loc[ user_sentiment_dataframe["User"] == user, tag] =  get_most_rated(pos,neg,neu)    #inserimento sulla tabella finale il valore maggiormente riscontrato
if not os.path.exists('sentiment_results'):
    os.makedirs('sentiment_results')
print("\nProcess terminated (Saved in \"sentiment_results/users_tags_table_"+library+".xlsx\" file)")
user_sentiment_dataframe.to_excel("sentiment_results/users_tags_table_"+library+".xlsx") 
print("\n(Saving all sentences in \"sentiment_results/sentences_"+library+".xlsx\" file)")
sentences_dataframe.to_excel("sentiment_results/sentences_"+library+".xlsx") 

