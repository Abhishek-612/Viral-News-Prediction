import pandas as pd
import newsapi
from news_crawler import custom_crawler_client,news_api_client
newsapi.NewsApiClient

df_news_api = news_api_client.run_api()
if df_news_api.empty:
    df_news_api = pd.read_csv(r'datasets/news-api-data.csv')

df_crawler = custom_crawler_client.run_crawler()
if df_crawler.empty:
    df_crawler = pd.read_csv(r'datasets/custom-crawler.csv')
#
# def create_crawler_dataframe(news_agency_list):
#     df = pd.DataFrame()
#     for agency in news_agency_list:
#         temp_df = pd.DataFrame(agency.get_articles(), columns=list(agency.get_articles().keys()))
#         df = pd.concat([df, temp_df], ignore_index=True)
#     return df
#
#
# if __name__ == "__main__":
#
#     with open('root_websites.txt','r') as f:
#         root_sites = [ x.replace('\n','') for x in f.readlines()]
#         f.close()
#
#     no_of_pages = 10
#
#     crawler = Crawler(root_sites, no_of_pages)
#     news_agency_list = crawler.get_news_agency_list()
#
#     df = create_crawler_dataframe(news_agency_list)
#     df = df.drop_duplicates()
#
#     # Save to csv for later use
#     df.to_csv('custom-crawler-data.csv', index=False)
