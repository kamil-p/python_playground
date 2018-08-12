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
