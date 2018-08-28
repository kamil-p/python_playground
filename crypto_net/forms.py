import io
import json
import logging
import time
from datetime import datetime

import matplotlib.pyplot as plt
import requests
from django.db.utils import IntegrityError
from django.forms import forms

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
            return int(time.time())

    @staticmethod
    def get_history_plot():
        history_by_minute = HistoryByMinute.get_avg_prices_with_time()

        def to_string_date(x):
            return datetime.utcfromtimestamp(x)

        x_time = []
        y_high = []

        for minute in history_by_minute:
            x_time.append(to_string_date(minute.time))
            y_high.append(minute.high)

        fig = plt.figure(1, figsize=(9, 4))
        plt.subplot(111)
        plt.plot(x_time, y_high)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        return buf


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
