import os
import pandas as pd
from news_crawler.websites_crawler import Crawler


def create_crawler_dataframe(news_agency_list):
    df = pd.DataFrame()
    for agency in news_agency_list:
        temp_df = pd.DataFrame(agency.get_articles(), columns=list(agency.get_articles().keys()))
        df = pd.concat([df, temp_df], ignore_index=True)
    return df


def run_crawler(no_of_pages = 1):
    with open('news_crawler/root_websites.txt','r') as f:
        root_sites = [ x.replace('\n','') for x in f.readlines()]
        f.close()

    crawler = Crawler(root_sites, no_of_pages)
    news_agency_list = crawler.get_news_agency_list()

    df = create_crawler_dataframe(news_agency_list)
    df = df.drop_duplicates()
    df = df.dropna()

    # Save to csv for later use
    if df.empty:
        df.to_csv(os.path.join('datasets',r'custom-crawler-data.csv'), index=False)
    return df