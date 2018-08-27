
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
    buf = HistoryByMinuteForm.get_history_plot()
    return HttpResponse(buf.getvalue(), content_type='image/png')
