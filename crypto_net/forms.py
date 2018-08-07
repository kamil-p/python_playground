from django.forms import forms
import requests
import json


class HistoryByMinuteForm(forms.Form):
    @staticmethod
    def sync_history():
        params = {'fsym': 'ETH', 'tsym': 'PLN', 'limit': 100}
        response = requests.get("https://min-api.cryptocompare.com/data/histominute", params)
        return response
