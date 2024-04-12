from tweepy import Cursor, Client

import api_credentials

import pandas as pd
import numpy as np
import re
import datetime

import warnings
warnings.filterwarnings("ignore")


class TwitterClient:
  def __init__(self, twitter_user=None):
    self.authenticate_twitter()
    
    self.twitter_user = twitter_user

  def authenticate_twitter(self):
        try:
          self.twitter_client = Client(bearer_token=api_credentials.BEARER_TOKEN)
          
          print('Twitter Authentication successful -', self.twitter_client)
        except:
          print('Twitter Authentication unsuccessful')

  def fetch_related_tweets(self,query, num_tweets=50):
    tweets = []
    try:
        end_date = datetime.date.today().strftime('%Y-%m-%d')

        response = self.twitter_client.search_recent_tweets(query=query, end_time=end_date, max_results=num_tweets, tweet_fields=["created_at", "text", "favorite_count", "retweet_count"])

        if response.data:
            tweets.extend(response.data)
    except Exception as e:
        print(e)
        

    return tweets


class TweetAnalyser:
    def clean_tweet(self, tweet):
        return ' '.join(re.sub('(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+\/\/\S+)', " ", tweet).split())

    def tweets_to_df(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['tweet'])

        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])

        return df
