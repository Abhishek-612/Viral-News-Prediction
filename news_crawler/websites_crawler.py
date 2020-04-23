from urllib.parse import urlparse
from news_crawler.news_article import News
from lxml import html
import requests, re


class Crawler:
    def __init__(self, root_sites, no_of_pages):
        self.root_sites = root_sites
        self.no_of_pages = no_of_pages

        self.websites = self.load_websites()
        self.agencies = self.get_agencies()
        self.news_agency_list = self.crawl_top_headlines()

    def load_websites(self):
        websites = list()
        for each in self.root_sites:
            for i in range(self.no_of_pages):
                if i == 0:
                    websites.append(each[:each.rindex('/')])
                else:
                    websites.append(each.format(i + 1))
        return websites

    def get_agencies(self):
        agency_list = list()
        for website in self.websites:
            domain = Crawler.extract_domain(website)
            if domain not in agency_list:
                agency_list.append(domain)
        return agency_list

    def crawl_top_headlines(self):
        news_agency_list = []
        for agency in self.agencies:
            headlines = []
            links = []
            news_agency = News(agency)
            for site in self.websites:
                if Crawler.extract_domain(site) == news_agency.agency:
                    page = requests.get(site)
                    tree = html.fromstring(page.content)
                    if agency == 'www.ndtv.com':
                        headlines.extend(
                            [news.replace('\n', '').strip() for news in
                             tree.xpath('//div[@class="nstory_header"]/a/text()') if
                             re.search(r"[A-Za-z0-9]", news.replace('\n', '').strip())])
                        links.extend(
                            [news.replace('\n', '').strip() for news in
                             tree.xpath('//div[@class="nstory_header"]/a/@href')])
                    elif agency == 'timesofindia.indiatimes.com':
                        headlines.extend(tree.xpath('/html/body/div/div[8]/div/div[2]/div[1]/ul[1]/li/a/@title'))
                        links.extend(['https://{}{}'.format(agency, x) if not x.startswith('https://') else x for x in
                                      tree.xpath('/html/body/div/div[8]/div/div[2]/div[1]/ul[1]/li/a/@href')])

            print(agency, '\n')
            news_agency.add_initial_details(headlines, links)
            news_agency.add_articles()
            print('\nUpdated {} latest headlines by {}'.format(len(news_agency.articles), news_agency.agency))
            news_agency_list.append(news_agency)
            print()

        return news_agency_list

    def get_news_agency_list(self):
        return self.news_agency_list

    @staticmethod
    def extract_domain(url, remove_http=True):
        uri = urlparse(url)
        if remove_http:
            domain_name = f"{uri.netloc}"
        else:
            domain_name = f"{uri.netloc}://{uri.netloc}"
        return domain_name
