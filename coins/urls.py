from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
import viewsets

router = DefaultRouter()
router.register(r'mints', viewsets.MintViewSet)
router.register(r'countries', viewsets.CountryViewSet)
router.register(r'currencies', viewsets.CurrencyViewSet)
router.register(r'collections', viewsets.CollectionViewSet)

urlpatterns = patterns('coins.views',
    url(
        r'^image\/(.+?)(?:[.](\d+)x(\d+))?(?:[.](jpg|jpeg|png|gif))?$',
        'image',
        name = 'show-image'
    ),
    url(
        r'^(?i)(coin|banknote)\/barcode\/(\d+)(?:[.](qr|code128))?(?:[.](jpg|jpeg|png|gif))?$',
        'barcode',
        name = 'barcode'
    ),
    url(
        r'^box\/(\d+)(?:[.](html|pdf))?$',
        'box'
    ),
    url(r'^$', TemplateView.as_view(template_name='index.html')),
    url(r'^', include(router.urls))
)