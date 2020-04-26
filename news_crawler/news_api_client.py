from newsapi import NewsApiClient
import requests, os
import pandas as pd
import nltk

try:
    nltk.data.find('tokenizer/punkt')
except LookupError:
    nltk.download('punkt')
from nltk.corpus import stopwords

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

key = '0b74da0a4fd14dfb9500bcc33685ba6d'
with requests.Session() as session:
    newsapi = NewsApiClient(api_key=key, session=session)


def create_dataframe(articles):
    df = pd.DataFrame()
    for article in articles['articles']:
        df1 = pd.DataFrame.from_dict(article)
        df1.insert(0, 'name', article['source']['name'])
        df1.insert(6, 'date', article['publishedAt'][:10])
        keywords = ','.join(set((str(article['title']) + ' ' + str(article['description'])).split()))
        df1.insert(7, 'keywords', keywords)
        df1['content'] = str(article['description']) + ' ' + str(article['content'])
        df1 = df1.drop(columns=['source', 'author', 'urlToImage', 'description', 'publishedAt'])
        df = pd.concat([df, df1], ignore_index=True)
    return df


def get_articles(headlines_df):
    import datetime

    today = datetime.datetime.today()
    before_15_days = today - datetime.timedelta(15)

    keywords_set = set()
    for k in headlines_df['keywords']:
        keywords_set.update(k.split(','))

    keywords = [word for word in keywords_set if word not in set(stopwords.words('english')) and word.isalpha()]

    with requests.Session() as session:
        all_articles = []
        for keyword in keywords:
            try:
                articles = newsapi.get_everything(q=keyword,
                                                  from_param=today.strftime('%Y-%m-%d'),
                                                  to=before_15_days.strftime('%Y-%m-%d'),
                                                  language='en',
                                                  sort_by='relevancy')
                all_articles.append(articles)
            except:
                print('API request limit exceeded! Try after 12 hours. \nContinuing with already retrieved data...')
                break

    df = pd.DataFrame()
    for article in all_articles:
        temp_df = create_dataframe(article)
        df = pd.concat([df, temp_df], ignore_index=True)

    return df


def run_api():
    df = pd.DataFrame()

    try:
        top_headlines = newsapi.get_top_headlines(language='en')
        df = create_dataframe(top_headlines)

        df1 = get_articles(df)
        df = pd.concat([df, df1], ignore_index=True)

        df = df.drop_duplicates()
        df = df.dropna()

    except:
        print('API request limit exceeded! Try after 12 hours. \nContinuing with already retrieved data...')

    if not df.empty:
        df.to_csv(os.path.join('datasets', r'news-api-data.csv'), index=False)

    return df
