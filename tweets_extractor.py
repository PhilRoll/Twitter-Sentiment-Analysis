import sys
import os
import time
import tweepy
import pandas as pd
import nltk
import requests
import numpy as np
from tweepy import OAuthHandler
from tweepy import Cursor

#chiave di accesso API V2 Twitter
bearer = #ADD API KEY

#client per accesso alle API Twitter
client = tweepy.Client(bearer_token=bearer, wait_on_rate_limit=True)

#Funzione che salva in formato CSV un dataframe
def save_df(df):
    if not os.path.exists('dataframes'):
        os.makedirs('dataframes')
    if not os.path.exists("dataframes/tweets.csv"):
        df.to_csv("dataframes/tweets.csv", mode='a', index=False) #salvare il dataframe in un CSV (MODALITA APPEND)
    else:
        df.to_csv("dataframes/tweets.csv", mode='a', index=False, header=False) #salvare il dataframe in un CSV (MODALITA APPEND)


#Restituisce l'ID di un utente Twitter
def get_user_id(screen_name):
    user = client.get_users(usernames=screen_name)
    return user.data[0].id


#Restituisce lo screen_name di un utente 
def get_user_screen_name(id):
    user = client.get_users(ids=id)
    return user.data[0].username


"""def get_recent_tweets(keyword, count_tweet):
    query = keyword+" lang:en -is:retweet -is:reply"
    tweets = []
    for tweet in tweepy.Paginator(client.search_recent_tweets, 
                                query=query,
                                tweet_fields=['author_id','text'], 
                                max_results=100).flatten(limit=count_tweet):
        tweets.append(tweet)

    result = []

    for tweet in tweets:
        result.append({'User': get_user_screen_name(tweet.author_id),
                    'Tweet': tweet.text, 
                    'lang': tweet.lang})

    if len(result)!=0:
        df = pd.DataFrame(result)
        print("found "+str(len(df))+" tweets")
        save_df(df)
        print("(saved on dataframe)\n")
    else:
        print("no tweets found\n")"""




#Restituisce la user timeline di un utente, restituisce fino a 3200tweets piu recenti
#se si escludono retweets e/o replies restituisce fino a 800tweets piu recenti
def get_user_tweets(username,count_tweet):
    print("scanning for "+username+" :")
    tweets = []
    for tweet in tweepy.Paginator(client.get_users_tweets, 
                                id= get_user_id(username), 
                                tweet_fields=['text','lang'], 
                                exclude=["retweets","replies"]).flatten(limit=count_tweet):
        
        tweets.append(tweet)

    result = []

    for tweet in tweets:
        result.append({'User': username,
                    'Tweet': tweet.text, 
                    'lang': tweet.lang})

    if len(result)!=0:
        df = pd.DataFrame(result)
        print("found "+str(len(df))+" tweets")
        save_df(df)
        print("(saved on dataframe)\n")
    else:
        print("no tweets found\n")
    

#Restituisce una lista di followers di un utente (max 1000)
def get_user_followers(username, count_tweet, page_limit):
    user_list = []
    for users in tweepy.Paginator(client.get_users_followers,
                                id=get_user_id(username),
                                max_results=count_tweet, 
                                limit=page_limit):

        if users.data is not None:
            for user in users.data:
                user_list.append(user.username)
        
    return user_list


#Restituisce una lista di amici (following) di un utente (max 1000)
def get_user_friends(username, count_tweet, page_limit):
    user_list = []
    for users in tweepy.Paginator(client.get_users_following, 
                                id=get_user_id(username), 
                                max_results=count_tweet, 
                                limit=page_limit):
                                
        if users.data is not None:
            for user in users.data:
                user_list.append(user.username)
        
    return user_list


#Funzione che restituisce la lista degli utenti dei tweets salvati
def get_users_list_from_df(df):
    all_user_list = df["User"].astype('string').tolist() #lista di utenti
    return list(np.unique(all_user_list))


#
# ESTRAZIONE DEI TWEETS:
#


print("searching users from brands page:")
#lista di account di twitter dei vari brand
twitter_brand_list = ["AlfaRomeoUSA", "SamsungUS", "lavazzaUSA","armani","adidasUS","Microsoft","BarillaUS","FerreroUK", "DeLonghiUK", "MuseoAmarelli"]

#per tutti i brand cerco 50 followers per brand
all_user_list = []
for twitter_brand in twitter_brand_list:
    all_user_list.extend(get_user_followers(twitter_brand,200,1))

#elimino i duplicati
users = list(np.unique(all_user_list)).sort()
print("find "+str(len(users))+" users.")

#Ricerca di tweets per ogni utente (Tweets dalla USERS TIMELINE)
print("Scanning for USERS: [",len(all_user_list)," users found]")
for username in all_user_list:
    get_user_tweets(username,3200)

df = pd.read_csv("dataframes/tweets.csv")
print("\nEND OF PROCESS:\n(find: "+str(len(df))+" tweets)")
print(str(len(get_users_list_from_df(df)))+" users found")

