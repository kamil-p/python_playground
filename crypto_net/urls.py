from django.urls import path

from . import views

app_name = 'crypto_net'
urlpatterns = [
    # ex: /crypto_net/
    path('', views.IndexView.as_view(), name='index'),
    path('sync_history', views.sync_history, name='sync_history'),
    path('get_price_history_plot.png', views.get_price_history_plot, name='get_price_history_plot'),
    path('get_price_linear_plot.png', views.get_price_linear_plot, name='get_price_linear_plot'),
]