from django.views import generic


class IndexView(generic.TemplateView):
    template_name = 'crypto_net/index.html'
