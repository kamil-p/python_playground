from django.http import HttpResponse
from django.views import generic

from .forms import NeuralNetworkForm


class IndexView(generic.TemplateView):
    template_name = 'neural_network/index.html'


def get_price_linear_plot(request):
    buf = NeuralNetworkForm.get_price_linear_regression_plot()
    return HttpResponse(buf.getvalue(), content_type='image/png')
