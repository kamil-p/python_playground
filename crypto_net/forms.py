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
    def get_price_linear_regression_plot():
        x_time = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=np.float64)
        y_price = np.array([1000, 1150, 1200, 1375, 1425, 1500, 1700, 1715, 1800, 1900], dtype=np.float64)

        fig = plt.figure(1, figsize=(9, 4))
        plt.subplot(111)
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.title("ETH/PLN - price history")
        plt.plot(x_time, y_price, '*', label='Price AVG')

        learning_rates = [
            {"rate": 0.000001, "plot": "--r"},
            {"rate": 0.00001, "plot": "--g"},
            {"rate": 0.0001, "plot": "--y"},
            {"rate": 0.001, "plot": "--o"},
            {"rate": 0.0025, "plot": "--p"},
        ]

        for learning_rate in learning_rates:
            HistoryByMinuteForm.add_linear_plot(x_time, y_price, learning_rate)
        plt.legend()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        return buf

    @staticmethod
    def add_linear_plot(x_time, y_price, learning_rate):
        error = 0
        np.array(x_time, dtype=np.float64)

        m = tf.Variable(0.39)
        b = tf.Variable(0.2)

        for x, y in zip(x_time, y_price):
            y_hat = m * x + b
            error += (y - y_hat) ** 2
        optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate["rate"])
        train = optimizer.minimize(error)
        init = tf.global_variables_initializer()
        session = tf.Session()

        with session as sess:
            sess.run(init)
            epochs = 100
            for i in range(epochs):
                sess.run(train)
            final_slope, final_intercept = sess.run([m, b])

        y_pred_plot = final_slope * x_time + final_intercept
        plt.plot(x_time, y_pred_plot, learning_rate["plot"], label='Learning rate {}'.format(learning_rate["rate"]))


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
