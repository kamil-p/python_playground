from django.db import models
from django.db import connection


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
            cursor.execute("SELECT h.time, (h.high+h.low)/2 AS price FROM crypto_net_historybyminute h")
        all = cursor.fetchall()
        return all
