import pandas as pd
import os
from viral_news_check import ViralNewsCheck
from news_crawler import custom_crawler_client, news_api_client

# df_news_api = news_api_client.run_api()
# if df_news_api.empty:
#     df_news_api = pd.read_csv(r'datasets/news-api-data.csv')
#
# df_crawler = custom_crawler_client.run_crawler()
# if df_crawler.empty:
#     df_crawler = pd.read_csv(r'datasets/custom-crawler.csv')

df_news_api = pd.read_csv(os.path.join('datasets',r'news-api-data.csv'))
df_crawler = pd.read_csv(os.path.join('datasets',r'custom-crawler-data.csv'))

df_all = pd.concat([df_news_api, df_crawler], ignore_index=True)

vnc = ViralNewsCheck(df_all)
vnc.build_w2v_model()

for title in df_all['title'][:10]:
    vnc.find_similar(title)
