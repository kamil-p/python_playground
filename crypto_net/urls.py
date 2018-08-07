from django.urls import path

from . import views

app_name = 'crypto_net'
urlpatterns = [
    # ex: /crypto_net/
    path('', views.IndexView.as_view(), name='index'),
    path('sync_history', views.sync_history, name='sync_history'),
]