import pandas as pd
from news_crawler.websites_crawler import Crawler


def create_dataframe(news_agency_list):
    df = pd.DataFrame()
    for agency in news_agency_list:
        temp_df = pd.DataFrame(agency.get_articles(), columns=list(agency.get_articles().keys()))
        df = pd.concat([df, temp_df], ignore_index=True)
    return df


if __name__ == "__main__":

    with open('root_websites.txt','r') as f:
        root_sites = [ x.replace('\n','') for x in f.readlines()]
        f.close()

    no_of_pages = 1

    crawler = Crawler(root_sites, no_of_pages)
    news_agency_list = crawler.get_news_agency_list()

    df = create_dataframe(news_agency_list)
    # Save to csv for later use
    df.to_csv(r'data.csv', index=False)
