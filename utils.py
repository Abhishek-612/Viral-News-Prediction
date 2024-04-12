import nltk
from nltk.tokenize import word_tokenize
from textblob import TextBlob
import warnings
warnings.filterwarnings("ignore")
from nltk.corpus import stopwords
nltk.download('brown')


def get_content_list(dataframe):
    titles_list = list(str(x) for x in dataframe['title'] if x )
    content_list = list(str(x) for x in dataframe['content'])

    return titles_list, content_list

def get_max(li):
    mx = min(li)
    for l in li:
        if 0.99 > l > mx:
            mx = l
    return (((mx * 10)) // 1) / 10

def filter_lines(line_list):
    new_list = list()
    for line in line_list:
        line_string = ' '.join(TextBlob(line).noun_phrases)
        new_list.append((line_string))

    return new_list

def preprocess(text):
    text = str(text).lower()
    doc = word_tokenize(text)
    doc = [word for word in doc if word not in set(stopwords.words('english'))]
    doc = [word for word in doc if word.isalpha()]
    return doc


def has_vector_representation(word2vec_model, doc):
    return not all(word not in word2vec_model.wv.index_to_key for word in doc)


def filter_docs(corpus, texts, condition_on_doc):
    number_of_docs = len(corpus)

    if texts is not None:
        texts = [text for (text, doc) in zip(texts, corpus)
                 if condition_on_doc(doc)]

    corpus = [doc for doc in corpus if condition_on_doc(doc)]
    print("{} docs removed".format(number_of_docs - len(corpus)))
    return (corpus, texts)


def generate_corpus(model,word_collection):
    corpus = [preprocess(title) for title in word_collection]
    corpus, word_collection = filter_docs(corpus, word_collection, lambda doc: has_vector_representation(model, doc))
    corpus, word_collection = filter_docs(corpus, word_collection, lambda doc: (len(doc) != 0))
    return word_collection


def fetch_all_words(word_collection):
    text_string = ' '.join(word_collection)
    # print(len(text_string))
    tokens = word_tokenize(text_string)

    words = list(set([str(word).lower() for word in tokens if not word.lower() in set(stopwords.words('english'))]))

    return words


def unique(list1):
    unique_list = []

    for x in list1:
        y = list1.index(x)
        if y not in unique_list:
            unique_list.append(y)
    return unique_list
