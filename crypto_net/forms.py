import json
import time

import requests
from django.forms import forms

from .models import HistoryByMinute


class HistoryByMinuteForm(forms.Form):
    @staticmethod
    def sync_history():
        lastHistory = HistoryByMinute.objects.latest('time')

        ts = int(time.time())
        params = {'fsym': 'ETH', 'tsym': 'PLN', 'limit': 100, 'toTS': ts}

        response = requests.get("https://min-api.cryptocompare.com/data/histominute", params)

        result = json.loads(response.text)

        # TODO extract to method
        one_history = result['Data'][0]
        one_history['crypto'] = 'ETH'
        one_history['curr'] = 'PLN'
        histo = HistoryByMinute.objects.create(**one_history)
        histo.save()

        return response
