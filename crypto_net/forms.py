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
        x = json.loads(response.text, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
        HistoryByMinute.objects.create(x.Data[0], crypto='ETH', curr='PLN')
        #histo = HistoryByMinute(
        #    time=x.Data[0].time,
        #    high=x.Data[0].high,
        #    low=x.Data[0].low,
        #    open=x.Data[0].open,
        #    close=x.Data[0].close,
        #    volumefrom=x.Data[0].volumefrom,
        #    volumeto=x.Data[0].volumeto,
        #    crypto='ETH',
        #    curr='PLN')

        histo.save()

        return response
