import datetime
import json
import time

import requests
from dateutil.relativedelta import *
from django.db.utils import IntegrityError
from django.forms import forms

from .models import HistoryByMinute


class HistoryByMinuteForm(forms.Form):
    @staticmethod
    def sync_history():
        try:
            lastHistory = HistoryByMinute.objects.latest('time')
            h_time = lastHistory.time
        except HistoryByMinute.DoesNotExist:
            h_time = int((datetime.datetime.now() - relativedelta(months=1)).timestamp())

        ts = None

        i = 0
        error_count = 0
        # TODO fix this infinity loop
        while (ts is None) or (h_time < ts):
            if ts is None:
                ts = int(time.time())
            else:
                ts = -5000

            params = {'fsym': 'ETH', 'tsym': 'PLN', 'limit': 100, 'toTS': ts}

            response = requests.get("https://min-api.cryptocompare.com/data/histominute", params)
            i = +1
            result = json.loads(response.text)

            for one_history in result['Data']:
                ts = one_history['time']
                one_history['crypto'] = 'ETH'
                one_history['curr'] = 'PLN'
                try:
                    histo = HistoryByMinute.objects.create(**one_history)
                    histo.save()
                except IntegrityError:
                    error_count = +1
                    print(error_count)

        return None
