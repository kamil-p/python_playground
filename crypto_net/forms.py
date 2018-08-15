import datetime
import json
import logging
import time

import requests
from dateutil.relativedelta import *
from django.db.utils import IntegrityError
from django.forms import forms

from .models import HistoryByMinute

logger = logging.getLogger('django')


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

        all_count = 0
        error_count = 0
        total_calls = 0

        while (ts is None) or (ts_now > ts):
            ts += 5000
            params = {'fsym': 'ETH', 'tsym': 'PLN', 'limit': 100, 'toTs': ts}

            response = requests.get("https://min-api.cryptocompare.com/data/histominute", params)
            total_calls += 1
            result = json.loads(response.text)

            logger.info("Total calls {}, row count {}, "
                        "successfully saved {}, error count {}".format(
                total_calls, all_count,
                all_count - error_count, error_count))

            for one_history in result['Data']:
                all_count += 1
                ts = one_history['time']
                one_history['crypto'] = 'ETH'
                one_history['curr'] = 'PLN'
                try:
                    history = HistoryByMinute.objects.create(**one_history)
                    history.save()
                except IntegrityError:
                    error_count += 1

        logger.info("Total calls {}, row count {}, "
                    "successfully saved {}, error count {}".format(
            total_calls, all_count,
            all_count - error_count, error_count))

        return None
