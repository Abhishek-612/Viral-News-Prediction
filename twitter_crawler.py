from tweepy import OAuthHandler
from tweepy import API, Cursor

import api_credentials

import pandas as pd
import numpy as np
import re

import warnings
warnings.filterwarnings("ignore")


class TwitterAuthenticator:

    def authenticate_twitter(self):
        auth = OAuthHandler(api_credentials.CONSUMER_KEY, api_credentials.CONSUMER_SECRET)
        auth.set_access_token(api_credentials.ACCESS_TOKEN, api_credentials.ACCESS_TOKEN_SECRET)
        return auth


class TwitterClient:
  def __init__(self, twitter_user=None):
    self.auth=TwitterAuthenticator().authenticate_twitter()
    self.twitter_client = API(self.auth)

    self.twitter_user = twitter_user

  def fetch_related_tweets(self,query, num_tweets=250):
    tweets = []
    import datetime
    try:
        for tweet in Cursor(self.twitter_client.search, q=query, until=datetime.date.today(), lang="en").items(num_tweets):
          tweets.append(tweet)
    except:
        print('Tweepy error - Request limit exceeded. Try in some time')

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
