import pandas as pd
import os, glob, shutil, re, time
import operator
from textblob import TextBlob
from viral_news_check import ViralNewsCheck
from news_crawler import custom_crawler_client, news_api_client
from twitter_crawler import TwitterClient, TweetAnalyser
from fbprophet_prediction import FBProphetPredictor
import nltk

nltk.download('brown')
import warnings

warnings.filterwarnings("ignore")

CRAWL_NEW_DATA = False

TWITTER_WEIGHT = 0.7
TRAIN_FURTHER = False
MODEL_LIMIT = None  # 2_000_000  (only top 2 million word embeddings)
# Line 63 has more parameters


try:
    if os.path.exists('results'):
        shutil.rmtree('results')
except:
    print('Please re-run the script')

if not os.path.exists('datasets/news-api-data.csv') and not os.path.exists('datasets/custom-crawler.csv'):
    CRAWL_NEW_DATA = True

if CRAWL_NEW_DATA:
    df_news_api = news_api_client.run_api()
    if df_news_api.empty:
        df_news_api = pd.read_csv(r'datasets/news-api-data.csv')

    df_crawler = custom_crawler_client.run_crawler()
    if df_crawler.empty:
        df_crawler = pd.read_csv(r'datasets/custom-crawler.csv')
else:
    df_news_api = pd.read_csv(os.path.join('datasets', r'news-api-data.csv'))
    df_crawler = pd.read_csv(os.path.join('datasets', r'custom-crawler-data.csv'))

df_all = pd.concat([df_news_api, df_crawler], ignore_index=True)
df_all.drop_duplicates(inplace=True)
df_all.dropna(inplace=True)

if os.path.exists('models'):
    PATH = glob.glob('models/*.model')[0]
else:
    PATH = None

vnc = ViralNewsCheck(df_all)

vnc.build_w2v_model(PATH, train_further=TRAIN_FURTHER, limit=MODEL_LIMIT)
vnc.calculate_feature_vectors()
print()

headline_score = dict()
sorted_df_all = df_all.sort_values(by='date', ascending=False)

NUM_W2V_HEADLINES = len(sorted_df_all)
FETCH_TOP_NEWS = len(sorted_df_all)
TIME_SLEEP = 60

for i in range(NUM_W2V_HEADLINES):  # Adjust NUM_W2V_HEADLINES if taking too long
    try:
        score = vnc.find_similar(sorted_df_all['title'][i])
        headline_score[sorted_df_all['title'][i]] = score
    except:
        continue

print('Obtained Headline Scores\nPlease check the results directory.')
sorted_headlines = sorted(headline_score.items(), key=operator.itemgetter(1), reverse=True)[:FETCH_TOP_NEWS]

if not os.path.exists('results/top headlines'):
    os.makedirs('results/top headlines')

twitter_client = TwitterClient()
tweet_analyser = TweetAnalyser()

for title, score in sorted_headlines:
    blob = TextBlob(title)
    q = ' '.join(blob.noun_phrases)
    tweet_score = 0
    date = None
    score = score * (1 - TWITTER_WEIGHT) * 100
    dir_name = re.sub(r'[^\w\s]', '', title)
    try:
        tweets = twitter_client.fetch_related_tweets(q)
        df = tweet_analyser.tweets_to_df(tweets)
        df.drop_duplicates(inplace=True)
        if df.size == 0:
            continue
        if not os.path.exists('results/top headlines/' + dir_name):
            os.makedirs('results/top headlines/' + dir_name)
        df.to_csv(os.path.join('results/top headlines/' + dir_name, 'tweets.csv'), index=False)

        predictor = FBProphetPredictor(df)
        predictor.predict(title)
        tweet_score = predictor.score * TWITTER_WEIGHT * 100
        date = predictor.date
    except:
        print('Tweepy limit exceeded, try in some time')

    try:
        if not os.path.exists('results/results.csv'):
            with open('results/results.csv', 'w') as f:
                f.write('Title,' + 'W2V Score({}%),'.format((1 - TWITTER_WEIGHT) * 100) + 'Twitter Score({}%),'.format(
                    TWITTER_WEIGHT * 100) + 'Virality(%),Viral by\n')
                f.close()

        with open('results/results.csv', 'a') as f:
            f.write(str(title).replace(',','') + ',' + str(score) + ',' + str(tweet_score) + ',' + str(score + tweet_score) + ',' + str(
                date) + '\n')
            f.close()
    except:
        pass

    time.sleep(TIME_SLEEP)
