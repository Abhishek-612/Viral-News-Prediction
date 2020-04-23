import datetime


class News:
    def __init__(self, agency):
        self.agency = agency
        self.headlines = []
        self.links = []
        self.articles = []

    def add_initial_details(self, headlines, links):
        self.headlines.extend(headlines)
        self.links.extend(links)

    def add_articles(self):
        for i in range(len(self.headlines)):
            article = Article(self.agency, self.headlines[i], self.links[i])
            if len(article.date) == 0:
                if len(self.articles) == 0:
                    article.date = datetime.datetime.now().strftime('%d/%m/%Y')
                else:
                    article.date = self.articles[-1].date
            if article.details_available == True and len(article.body) != 0:
                print(article.link+ ' added')
                self.articles.append(article)

    def get_articles(self):
        details_dict = dict()
        details_dict['agency'] = []
        details_dict['headline'] = []
        details_dict['link'] = []
        details_dict['date'] = []
        details_dict['keywords'] = []
        details_dict['body'] = []

        for article in self.articles:
            details_dict['agency'].append(article.agency)
            details_dict['headline'].append(article.headline)
            details_dict['link'].append(article.link)
            details_dict['date'].append(article.date)
            details_dict['keywords'].append(article.keywords)
            details_dict['body'].append(article.body)

        return details_dict


class Article:
    def __init__(self, agency, headline, link):
        self.agency = agency
        self.headline = headline
        self.link = link
        self.date = ''
        self.time = ''
        self.keywords = []
        self.body = []
        self.add_details()
        self.details_available = True

    def add_details(self):
        from lxml import html
        import requests, re

        import nltk
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')

        from nltk.corpus import stopwords
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')

        from nltk.tokenize import word_tokenize

        page = requests.get(self.link)
        tree = html.fromstring(page.content)

        text = ''
        if self.agency == 'www.ndtv.com':
            try:
                self.date = datetime.datetime.strptime([re.search(r'[0-9]*\s[A-Za-z]*\s[0-9]*', x).group(0) for x in
                                                        tree.xpath('//meta[@name="publish-date"]/@content')][0],
                                                       '%d %b %Y').strftime('%d/%m/%Y')
                self.time = \
                    [re.search(r'[0-9]*:[0-9]*', x).group(0) for x in
                     tree.xpath('//meta[@name="publish-date"]/@content')][
                        0]
            except:
                self.details_available = False
                self.date = ''

            try:
                self.keywords = [x for x in tree.xpath('//meta[@name="news_keywords"]/@content')][0].split(',')
            except:
                print('keyword error')
                self.details_available = False

            try:
                text = ''
                div_class = ['sp-cn ins_storybody', 'article__content h__mb40', 'articleBody',
                             'content_text row description', 'article_storybody']
                for div in div_class:
                    if div == 'articleBody':
                        loc = tree.xpath('//span[@itemprop="{}"]/p/text()'.format(div))
                        if len(loc) == 0:
                            loc = tree.xpath('//div[@itemprop="{}"]/div/p/text()'.format(div))
                    else:
                        loc = tree.xpath('//div[@class="{}"]/p/text()'.format(div))

                    if len(loc) == 0:
                        continue

                    text = ' '.join([x for x in loc]).strip()
            except:
                print('text error')
                self.details_available = False

        elif self.agency == 'timesofindia.indiatimes.com':
            try:
                import re
                x = tree.xpath('//div[@class="_3Mkg- byline"]/text()')[0]
                self.date = datetime.datetime.strptime(x[-24:-10].replace(',', '').strip(), '%b %d %Y').strftime(
                    '%d/%m/%Y')
                self.time = x[-9:-4]
            except:
                self.details_available = False
                self.date = ''

            try:
                self.keywords = [x for x in tree.xpath('//meta[@name="keywords"]/@content')][0].split(',')
            except:
                print('keyword error')
                self.details_available = False

            try:
                div_class = ['_3WlLe clearfix  ', 'Normal']
                text = ''
                for div in div_class:
                    loc = tree.xpath('//div[@class="{}"]/a/text()'.format(div))
                    if len(loc) == 0:
                        continue
                    new = [x for x in loc]
                    new.extend([x for x in tree.xpath('//div[@class="{}"]/text()'.format(div))])
                    text = ' '.join(new).strip()
            except:
                print('text error')
                self.details_available = False

        body_tokens = word_tokenize(text)
        self.body = list(set(map(lambda x: x.lower(), [word for word in body_tokens if not word in stopwords.words()])))
