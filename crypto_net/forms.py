import json
import logging
import time

import requests
from django.db.utils import IntegrityError
from django.forms import forms

from .models import HistoryByMinute

logger = logging.getLogger('django')


class HistoryByMinuteForm(forms.Form):
    @staticmethod
    def sync_history():
        ts = HistoryByMinuteForm.__get_start_ts()
        now = int(time.time())
        all_count = 0
        error_count = 0
        total_calls = 0

        while (ts is None) or (now >= ts):
            params = {'fsym': 'ETH', 'tsym': 'PLN', 'limit': 100, 'toTs': ts}

            total_calls += 1
            # TODO fix redundant call after retry of complete sync
            response = requests.get("https://min-api.cryptocompare.com/data/histominute", params)
            result = json.loads(response.text)

            logger.info("Total calls {}, row count {}, successfully saved {}, error count {}"
                        .format(total_calls, all_count, all_count - error_count, error_count))

            if 'TimeTo' in result:
                ts = result['TimeTo'] + 6060
            else:
                break

            for one_history in result['Data']:
                all_count += 1

                one_history['crypto'] = params['fsym']
                one_history['curr'] = params['tsym']

                try:
                    history = HistoryByMinute.objects.create(**one_history)
                    history.save()
                except IntegrityError:
                    error_count += 1

        logger.info("Total calls {}, row count {}, successfully saved {}, error count {}"
                    .format(total_calls, all_count, all_count - error_count, error_count))

        return None

    @staticmethod
    def __get_start_ts():
        try:
            last_history = HistoryByMinute.objects.latest('time')
            return last_history.time
        except HistoryByMinute.DoesNotExist:
            return int(time.time()) - 578400

    @staticmethod
    def get_data(*fields):
        result = {'time': HistoryByMinute.objects.values_list('time', flat=True), 'high': HistoryByMinute.objects.values_list('high')}
        return result
