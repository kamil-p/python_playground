import io
import json
import logging
import math
import time
import numpy as np
import tensorflow as tf
import requests
import matplotlib.pyplot as plt

from datetime import datetime
from django.db.utils import IntegrityError
from django.forms import forms
from tensorflow.python import debug as tf_debug

from .models import HistoryByMinute

logger = logging.getLogger('django')


class HistoryByMinuteForm(forms.Form):
    @staticmethod
    def sync_history():
        def sync_page(sync_counter):
            params = {'fsym': 'ETH', 'tsym': 'PLN', 'limit': 100, 'toTs': sync_counter.ts}

            sync_counter.add_total_call_count()
            response = requests.get("https://min-api.cryptocompare.com/data/histominute", params)
            result = json.loads(response.text)

            if 'TimeTo' in result:
                sync_counter.ts = result['TimeTo'] + 6060
            else:
                return

            for one_history in result['Data']:
                sync_counter.add_all_count()

                one_history['crypto'] = params['fsym']
                one_history['curr'] = params['tsym']

                try:
                    history = HistoryByMinute.objects.create(**one_history)
                    history.save()
                except IntegrityError:
                    sync_counter.add_error_count()

        now = int(time.time())
        sync_history_counter = SyncHistoryCounter(HistoryByMinuteForm.__get_start_ts())

        while (sync_history_counter.ts is None) or (now >= sync_history_counter.ts):
            sync_page(sync_history_counter)
            sync_history_counter.log_status()

        return None

    @staticmethod
    def __get_start_ts():
        try:
            last_history = HistoryByMinute.objects.latest('time')
            return last_history.time
        except HistoryByMinute.DoesNotExist:
            return int(time.time()) - 504800  # minus a week

    @staticmethod
    def get_price_history_plot():
        history_by_minute = HistoryByMinute.objects.order_by('-time').all()[:19000]

        x_time = []
        y_price = []
        y_price_diff = []

        for minute in history_by_minute:
            x_time.append(to_string_date(minute.time))
            y_price.append((minute.high + minute.low)/2)
            y_price_diff.append(math.fabs((minute.open - minute.close) * 5) + 500)

        fig = plt.figure(1, figsize=(9, 4))
        plt.subplot(111)
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.title("ETH/PLN - price history")
        plt.plot(x_time, y_price_diff, label='|Price diff| * 5 + 500')
        plt.plot(x_time, y_price, 'r', label='Price AVG')
        plt.legend()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        return buf

    @staticmethod
    def get_price_linear_plot():
        history_by_minute = HistoryByMinute.objects.order_by('-time').all()[:100:10]

        x_time = np.array([], dtype=np.float64)
        y_price = np.array([], dtype=np.float64)
        y_price_diff = []

        x_time = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=np.float64)
        y_price = np.array([1500, 1550, 1600, 1575, 1625, 1600, 1700, 1715, 1700, 1750], dtype=np.float64)

        # for minute in history_by_minute:
        #     x_time = np.append(x_time, minute.time)
        #     y_price = np.append(y_price, (minute.high + minute.low)/2)

        m = tf.Variable(0.39)
        b = tf.Variable(0.2)
        # x_time = np.linspace(0,10,10) + np.random.uniform(-1.5,1.5,10)
        # y_price = np.linspace(0,10,10) + np.random.uniform(-1.5,1.5,10)

        error = 0
        np.array(x_time, dtype=np.float64)
        for x, y in zip(x_time, y_price):
            y_hat = m * x + b  # Our predicted value
            error += (y - y_hat) ** 2  # The cost we want to minimize (we'll need to use an
            print(error)                       # optimization function for the minimization!)

        optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.0001)
        train = optimizer.minimize(error)

        init = tf.global_variables_initializer()
        session = tf.Session()
        # session = tf_debug.TensorBoardDebugWrapperSession(session, "Kamil:7000")
        with session as sess:
            sess.run(init)
            epochs = 100
            for i in range(epochs):
                sess.run(train)
                print("Iteration %d m: %s b: %s" % (i, m, b))


            #  Fetch Back Results
            final_slope, final_intercept = sess.run([m, b])

        print(final_slope)
        print(final_intercept)

        x_test = x_time

        y_pred_plot = final_slope * x_test + final_intercept

        fig = plt.figure(1, figsize=(9, 4))
        plt.subplot(111)
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.title("ETH/PLN - price history")
        plt.plot(y_pred_plot, y_price, 'r', label='Prediction')
        plt.plot(x_time, y_price, '*', label='Price AVG')
        plt.legend()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        return buf


def to_string_date(x):
    return datetime.utcfromtimestamp(x)


class SyncHistoryCounter:
    def __init__(self, ts):
        self.ts = ts
        self.total_calls_count = 0
        self.all_count = 0
        self.error_count = 0

    def add_total_call_count(self):
        self.total_calls_count += 1

    def add_all_count(self):
        self.all_count += 1

    def add_error_count(self):
        self.error_count += 1

    def log_status(self):
        logger.info("Total calls {}, row count {}, successfully saved {}, error count {}"
                    .format(self.total_calls_count, self.all_count, self.all_count - self.error_count,
                            self.error_count))
