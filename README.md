# Viral-News-Prediction
A complete project that fetches latest news and information from well-known online news websites and uses the outreach on social media as well as coverage by news agencies, to predict the degree to which the headline will get viral.

The [main.py](main.py) file is the main script file. Constraints may have to be adjusted as per use.

The project is divided in _three_ distinct components - 
1. **News Crawler**
2. **Detection of similar headlines**
3. **Social Media Impact Prediction (Twitter)**

### 1. News Crawler
The project implements two different methods of scraping news from the internet. The first is performed using the [News API](https://newsapi.org/). The second is a custom crawler but it can only fetch headlines from two websites currently, i.e.- NDTV and Times of India. However, it fetches news from all subsidaries of the domains, and will be updated soon for more. The custom crawler can adjust the number of pages to be scraped from the [main.py](main.py) file. The project uses both the crawling scripts since the latter has limited scope while the former may be limited by request rates of the API.

### 2. Detection of similar headlines
We use _Natural Language Processing_ using a ***Word2Vec*** model. Due to the limitation on the text corpus from the crawled data, we use existing word embeddings from the [Google News vectors](https://github.com/mmihaltz/word2vec-GoogleNews-vectors) which has pre-trained vectors for over 2 billion words. It is further trained with the vocabulary of the crawled text corpus. Adding to that, we create document vectors using the word embeddings for the text corpus. We use custom generated document vectors instead of Doc2Vec, since the combination of Word2Vec with this tweak provides a more pertinent result to our use case [[Ref. 1](https://towardsdatascience.com/using-word2vec-to-analyze-news-headlines-and-predict-article-success-cdeda5f14751)]. 

**IMPORTANT NOTE:** The model may take a lot of time to train for the first time since the GoogleNews vector set is extremely large! However, there are alternatives to this:
1. Add ***limit*** constraint to the [build_w2v_model()](viral_news_check.py) function.
2. Set the ***train_further*** constraint of the [build_w2v_model()](viral_news_check.py) function to **False**. This will not train the new vocabulary from the crawled corpus, and will have less impact on the training time, but it will surely reduce.
3. Use alternative environments such as [Google Colab](https://colab.research.google.com/). Loading in environments like JetBrains PyCharm may cause a MemoryError due to the limited amount of memory allocated to the environment. So, you may want to run the [main.py](main.py) script from the Terminal/Command Prompt

### 3. Social Media Impact Prediction
We use [Twitter](https://developer.twitter.com/en) as the platform to detect impact as it is known for public and sensitive discussions and hence gives a good analysis of their opinions, sentiments and impact. We use Twitter data to as a Time Series data of the number of tweets and retweets, on the subject of the crawled headlines, grouped _hourly_. Since headlines are recent, there isn't much data to make an accurate prediction. Hence, we use the [Facebook's Prophet](https://facebook.github.io/prophet/) which has a robust forecasting model trained over long time data of user responses with seasonal and holiday effects.

## Scoring 
Since we use two different approaches and environments to analyse the prediction, we use a scoring metric to calculate the virality. The idea of using score assignment was inspired by Roja Bandari et al [[Ref. 2](https://www.hpl.hp.com/research/scl/papers/newsprediction/pulse.pdf)]

The score assignment gives **40%** weightage to the Word2Vec model and **60%** to the Twitter data analysis for the next 7 days, since the scope of the former is limited to how many news sites cover the topic, while the latter provides an estimate of number of people who reacted to the topic. 

## References
1. https://towardsdatascience.com/using-word2vec-to-analyze-news-headlines-and-predict-article-success-cdeda5f14751
2. https://www.hpl.hp.com/research/scl/papers/newsprediction/pulse.pdf
