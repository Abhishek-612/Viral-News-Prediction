import nltk, os,re
import pandas as pd
try:
    nltk.data.find('tokenizer/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

import numpy as np
import warnings
warnings.filterwarnings("ignore")
from gensim.models import KeyedVectors, Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
from utils import *


MIN_LIMIT = 0.05

class ViralNewsCheck:

    def __init__(self, df):
        self.df = df
        self.df.drop_duplicates(inplace=True)
        self.titles, self.content = get_content_list(self.df)
        self.word_collection = list()
        self.word_collection.extend(self.titles)
        self.word_collection.extend(self.content)

    def build_w2v_model(self, path=None, train_further=True, limit=None):

        if train_further:
            words = fetch_all_words(self.word_collection)

            print('\nStage 1/6 : Creating a new model')
            self.model = Word2Vec(size=300, min_count=1)

            print('Stage 2/6 : Building vocabulary for custom corpus')
            self.model.build_vocab(words)
            total_examples = self.model.corpus_count

            print('Stage 3/6 : Loading pre-trained vectors')
            if path is None:
                model_old = KeyedVectors.load_word2vec_format("https://s3.amazonaws.com/dl4j-distribution/GoogleNews-vectors-negative300.bin.gz", binary=True,limit=limit)
            else:
                model_old = KeyedVectors.load(path)

            print('Stage 4/6 : Building vocabulary of the pre-trained model\'s words')
            self.model.build_vocab([list(model_old.wv.vocab.keys())], update=True)
            if path is None:
                self.model.intersect_word2vec_format("https://s3.amazonaws.com/dl4j-distribution/GoogleNews-vectors-negative300.bin.gz", binary=True, lockf=1.0)

            print('Stage 5/6 : Training the new model')
            self.model.train(words, total_examples=total_examples, epochs=10)

            print('Stage 6/6 : Saving the new model')
            if not os.path.exists('models'):
                os.makedirs('models')
            self.model.wv.save(os.path.join('models','viral-news-w2v.model'))

        else:
            print('\nNot training new words (Add parameter train_further = True in order to do so)')
            print('Stage 1/1 : Loading pre-trained vectors')
            if path is None:
                self.model = KeyedVectors.load_word2vec_format("https://s3.amazonaws.com/dl4j-distribution/GoogleNews-vectors-negative300.bin.gz", binary=True,limit=limit)
            else:
                self.model = KeyedVectors.load(path)

        print('\nDone!\n\n')

    def calculate_feature_vectors(self):
        word_collection = generate_corpus(self.model, self.word_collection)
        corpus = [preprocess(doc) for doc in word_collection]
        self.X = self.get_document_vectors(corpus)

    def generate_document_vector(self, doc):
        doc = [word for word in doc if word in self.model.wv.vocab]
        return np.mean(self.model[doc], axis=0)

    def get_document_vectors(self,corpus):
        x = list()
        for doc in corpus:
            x.append(self.generate_document_vector(doc))

        return np.array(x)

    def find_similar(self, title):
        print(title)
        val = cosine_similarity([self.X[self.titles.index(title)]], self.X)[0]
        max_val = get_max(val)
        d = list(zip(self.titles,val))
        d.sort(key=lambda tup: tup[1],reverse=True)


        indices = list(idx for idx,element in enumerate(d) if (max_val - MIN_LIMIT) < element[1] <= max_val)


        if len(indices) == 0:
            print('Found 0 similar headlines\n')
            return 0

        associated_news = list(element[0] for idx,element in enumerate(d[indices[0]: 1+(indices[9] if len(indices)>=10 else indices[-1])]))
        values = list(element[1] for idx,element in enumerate(d[indices[0]: 1+(indices[9] if len(indices)>=10 else indices[-1])]))

        if len(values) > 0:
            dir_name = re.sub(r'[^\w\s]','',title)
            if not os.path.exists('results/w2v_analysis/' + dir_name):
                os.makedirs('results/w2v_analysis/' + dir_name)
            df = pd.DataFrame(list(zip(associated_news,values)),columns=['Title','Probability'])
            df.to_csv(os.path.join('results/w2v_analysis/' + dir_name, 'w2v_result.csv'), index=False)

        print('Found '+str(len(values))+' similar headlines\n')
        score = len(values)/10

        return score
