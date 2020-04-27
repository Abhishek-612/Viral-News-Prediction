from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


def get_content_list(dataframe):
    all_titles = list(dataframe['title'])

    all_content = list(dataframe['content'])

    titles_list = [str(all_titles[x]) for x in unique(all_titles)]
    content_list = [str(all_content[x]) for x in unique(all_content)]

    # for t in titles_list:
    #     print(len(t))
    return titles_list, content_list


def preprocess(text):
    text = str(text).lower()
    doc = word_tokenize(text)
    doc = [word for word in doc if word not in set(stopwords.words('english'))]
    doc = [word for word in doc if word.isalpha()]
    return doc


def has_vector_representation(word2vec_model, doc):
    return not all(word not in word2vec_model.wv.vocab for word in doc)


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

    tokens = word_tokenize(text_string)
    words = [word.lower() for word in tokens if word.isalpha()]

    from nltk.corpus import stopwords
    words = list(set([word.lower() for word in words if not word.lower() in set(stopwords.words('english'))]))

    return words


def unique(list1):
    unique_list = []

    for x in list1:
        y = list1.index(x)
        if y not in unique_list:
            unique_list.append(y)
    return unique_list
