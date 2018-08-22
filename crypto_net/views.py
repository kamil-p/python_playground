import io

import matplotlib.pyplot as plt
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic

from .forms import HistoryByMinuteForm


class IndexView(generic.TemplateView):
    template_name = 'crypto_net/index.html'


def sync_history(request):
    HistoryByMinuteForm.sync_history()
    return HttpResponseRedirect(reverse('crypto_net:index'))


def get_history_plot(request):
    history = HistoryByMinuteForm.get_history_plot()

    fig = plt.figure(1, figsize=(9, 4))
    plt.subplot(111)
    plt.plot(history['time'], history['high'])
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    response = HttpResponse(buf.getvalue(), content_type='image/png')
    return response
