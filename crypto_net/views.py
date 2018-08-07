from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import HistoryByMinuteForm


class IndexView(generic.TemplateView):
    template_name = 'crypto_net/index.html'


def sync_history(request):
    HistoryByMinuteForm.sync_history()
    return HttpResponseRedirect(reverse('crypto_net:index'))
