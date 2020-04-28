import pandas as pd
import os, glob,shutil,re
import operator
from textblob import TextBlob
from viral_news_check import ViralNewsCheck
from news_crawler import custom_crawler_client, news_api_client
from twitter_crawler import TwitterClient,TweetAnalyser
from fbprophet_prediction import FBProphetPredictor
import nltk
nltk.download('brown')
import warnings
warnings.filterwarnings("ignore")

df_news_api = news_api_client.run_api()
if df_news_api.empty:
    df_news_api = pd.read_csv(r'datasets/news-api-data.csv')

df_crawler = custom_crawler_client.run_crawler()
if df_crawler.empty:
    df_crawler = pd.read_csv(r'datasets/custom-crawler.csv')

if os.path.exists('results/top headlines'):
    shutil.rmtree('results/top headlines')

# df_news_api = pd.read_csv(os.path.join('datasets',r'news-api-data.csv'))
# df_crawler = pd.read_csv(os.path.join('datasets',r'custom-crawler-data.csv'))

df_all = pd.concat([df_news_api, df_crawler], ignore_index=True)

if os.path.exists('models'):
    PATH = glob.glob('models/*.model')[0]
else:
    PATH = None

vnc = ViralNewsCheck(df_all)

vnc.build_w2v_model(PATH,train_further=True)
vnc.calculate_feature_vectors()
print()


headline_score = dict()
sorted_df_all = df_all.sort_values(by='date',ascending=False)
NUM_W2V_HEADLINES = len(sorted_df_all)

for i in range(NUM_W2V_HEADLINES):      #Adjust NUM_W2V_HEADLINES if taking too long
    score = vnc.find_similar(sorted_df_all['title'][i])
    headline_score[sorted_df_all['title'][i]] = score

print('Obtained Headline Scores')
sorted_headlines = sorted(headline_score.items(), key=operator.itemgetter(1), reverse=True)[:10]


if not os.path.exists('results/top headlines'):
    os.makedirs('results/top headlines')

twitter_client = TwitterClient()
tweet_analyser = TweetAnalyser()

final_scores=list()
w2v_scores=list()
twitter_scores = list()
top_viral_headlines = list()
viral_by = list()

for title,score in sorted_headlines:
    blob = TextBlob(title)
    q = ' '.join(blob.noun_phrases)
    tweet_score = 0
    dir_name = re.sub(r'[^\w\s]','',title)
    try:
        tweets = twitter_client.fetch_related_tweets(q)
        df = tweet_analyser.tweets_to_df(tweets)
        df.drop_duplicates(inplace=True)
        if df.size==0:
            continue
        if not os.path.exists('results/top headlines/' + dir_name):
            os.makedirs('results/top headlines/' + dir_name)
        df.to_csv(os.path.join('results/top headlines/' + dir_name,'tweets.csv'),index=False)

        predictor = FBProphetPredictor(df)
        predictor.predict(title)
        tweet_score = predictor.score

    finally:
        top_viral_headlines.append(title)
        w2v_scores.append(score)
        twitter_scores.append(tweet_score)
        final_scores.append(tweet_score + score)
        if tweet_score!=0:
            viral_by.append(predictor.date)
        else:
            viral_by.append('N/A')


print('\n****************')

result_df = pd.DataFrame(list(zip(top_viral_headlines,w2v_scores,twitter_scores,final_scores,viral_by)),
                         columns=['Title','W2V Score(40%)','Twitter Score(60%)','Virality(%)','Viral by'])
result_df.sort_values(by='Virality(%)',ascending=False,inplace=True)

print(result_df.head())
if not os.path.exists('results/top headlines/'):
    os.makedirs('results/top headlines/')
result_df.to_csv(os.path.join('results/top headlines/','results.csv'),index=False)

print('\nResults stored in the "results" directory')