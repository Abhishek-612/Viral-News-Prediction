import pandas as pd
import os,re
from fbprophet import Prophet
from matplotlib import pyplot as plt


class FBProphetPredictor:
    def __init__(self,data_init,tolerance=0.1):
        self.data_init = data_init
        self.data = self.data_init.drop(columns=['tweet', 'likes'])

        self.data = self.data.rename(columns={'date': 'ds', 'retweets': 'y'})
        self.data['ds'] = pd.to_datetime(self.data['ds'])

        d = self.data.resample('60min', on='ds').count()

        df = self.data.resample('60min', on='ds').sum()
        df['y'] = (df['y'] + d['y']) * (1 - tolerance)  # tolerance = 10%
        self.data = df.reset_index()
        self.score = 0

    def predict(self,title):
        m = Prophet(changepoint_prior_scale=0.15)
        train = self.data

        try:
            m.fit(train)

            self.prediction = m.predict(m.make_future_dataframe(periods=170, freq='H'))
            m.plot(self.prediction)
            m.plot(self.prediction)
            self.get_virality()
            plt.savefig(os.path.join('results/top headlines/'+re.sub(r'[^\w\s]','',title),str('twitter_graph.png')))
        except ValueError:
            if self.data_init.shape[0] < 5:
                print('Not enough data...Hence, not viral')
                self.score = 0
            else:
                self.score = 60
                self.date = self.data['ds'].max()


    def get_virality(self):
        first_day = self.data['ds'].min()
        last_day = self.data['ds'].max()
        delta = last_day - first_day
        day_factor = 1 + (1 / (delta.days + 1))

        trend_limit = self.prediction['yhat'][:len(self.data['y'])].median() * day_factor

        flag = False
        self.date = None
        prev = trend_limit
        for i in range(len(self.prediction['ds']) - len(self.data['ds'])):
            p = i + len(self.data['ds'])
            if self.prediction['yhat'][p] >= prev:
                flag = True
                prev = self.prediction['yhat'][(p - 24) if p>24 else 0:p].mean()
                if self.date is None:
                    self.date = self.prediction['ds'][p]
            else:
                flag = False
                self.date = None

        if flag:
            print('Viral by', self.date.strftime('%d/%m/%Y'))
        else:
            print('Not viral')

        self.calc_score()


    def calc_score(self):
        if self.date is not None:
            day = self.date
            day_delta = (self.prediction['ds'].max() - day).days + 1
            predicted_span = (self.prediction['ds'].max() - self.data['ds'].max()).days + 1

            self.score = (day_delta/predicted_span) if (day_delta/predicted_span)<1 else 1

    def get_score(self):
        return self.score