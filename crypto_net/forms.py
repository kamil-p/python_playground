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
            last_history = HistoryByMinute.objects.latest('time')
            ts = last_history.time
        except HistoryByMinute.DoesNotExist:
            ts = int((datetime.datetime.now() - relativedelta(weeks=1)).timestamp())
            ts -= 5000

        ts_now = int(time.time())

        i = 0
        error_count = 0
        while (ts is None) or (ts_now > ts):
            ts += 5000
            params = {'fsym': 'ETH', 'tsym': 'PLN', 'limit': 100, 'toTs': ts}

            response = requests.get("https://min-api.cryptocompare.com/data/histominute", params)
            i += 1
            result = json.loads(response.text)
            print("While count = " + i.__str__() + " response len = " + len(result['Data']).__str__())

            for one_history in result['Data']:
                ts = one_history['time']
                one_history['crypto'] = 'ETH'
                one_history['curr'] = 'PLN'
                try:
                    histo = HistoryByMinute.objects.create(**one_history)
                    histo.save()
                except IntegrityError:
                    error_count += 1
                    print(error_count)

        return None
