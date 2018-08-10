from django.forms import forms
from collections import namedtuple
from .models import HistoryByMinute
import requests
import json


class HistoryByMinuteForm(forms.Form):
    @staticmethod
    def sync_history():
        params = {'fsym': 'ETH', 'tsym': 'PLN', 'limit': 100}
        response = requests.get("https://min-api.cryptocompare.com/data/histominute", params)
        result = json.loads(response.text)
        one_history = result['Data'][0]
        one_history['crypto'] = 'ETH'
        one_history['curr'] = 'PLN'
        histo = HistoryByMinute.objects.create(**one_history)
        histo.save()

        return response
