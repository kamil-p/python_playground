import numpy as np
from django.db import connection
from django.db import models


class HistoryByMinute(models.Model):
    time = models.IntegerField(unique=True)
    high = models.IntegerField()
    low = models.IntegerField()
    open = models.IntegerField()
    close = models.IntegerField()
    volumefrom = models.IntegerField()
    volumeto = models.IntegerField()
    crypto = models.CharField(max_length=10)
    curr = models.CharField(max_length=10)

    @staticmethod
    def get_avg_prices_with_time():
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT to_timestamp(h.time) AT TIME ZONE 'UTC' as time, (h.high+h.low)/2 AS pric "
                "FROM crypto_net_historybyminute h "
                "ORDER BY time ASC"
            )
            return np.transpose(cursor.fetchall())
