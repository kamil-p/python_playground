from django.urls import path

from . import views

app_name = 'neural_network'
urlpatterns = [
    # ex: /neural_network/
    path('', views.IndexView.as_view(), name='index'),
    path('get_price_linear_plot.png', views.get_price_linear_plot, name='get_price_linear_plot'),
]