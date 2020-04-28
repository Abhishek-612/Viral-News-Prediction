import pandas as pd
import os, glob
from textblob import TextBlob
from viral_news_check import ViralNewsCheck
from news_crawler import custom_crawler_client, news_api_client
from twitter_crawler import TwitterClient,TweetAnalyser
from fbprophet_prediction import FBProphetPredictor


# df_news_api = news_api_client.run_api()
# if df_news_api.empty:
#     df_news_api = pd.read_csv(r'datasets/news-api-data.csv')
#
# df_crawler = custom_crawler_client.run_crawler()
# if df_crawler.empty:
#     df_crawler = pd.read_csv(r'datasets/custom-crawler.csv')


# df_news_api = pd.read_csv(os.path.join('datasets',r'news-api-data.csv'))
# df_crawler = pd.read_csv(os.path.join('datasets',r'custom-crawler-data.csv'))
#
# df_all = pd.concat([df_news_api, df_crawler], ignore_index=True)
# PATH=glob.glob('models/*.model')[0]
# vnc = ViralNewsCheck(df_all)
# vnc.build_w2v_model(PATH,train_further=False)
# vnc.calculate_feature_vectors()
#
# for title in df_all['title'][:10]:
#     vnc.find_similar(title)


# twitter_client = TwitterClient()
#
# title='India to produce covid-19 vaccines'
# import nltk
# nltk.download('brown')
# blob = TextBlob(title)
# q = ' '.join(blob.noun_phrases)
# print(q)
# tweets = twitter_client.fetch_related_tweets(q)
#
# tweet_analyser = TweetAnalyser()
# df = tweet_analyser.tweets_to_df(tweets)
#
# print(df.shape)


data = pd.read_csv('C:\\Users\\Revadekar\\Downloads\\tweet (8).csv')
predictor = FBProphetPredictor(data)
predictor.predict()
print(predictor.score)