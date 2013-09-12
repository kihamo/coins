from django.conf.urls import patterns, url, include
from viewsets import MintViewSet, CountryViewSet, CurrencyViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'mints', MintViewSet)
router.register(r'countries', CountryViewSet)
router.register(r'currencies', CurrencyViewSet)

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
    url(r'^', include(router.urls))
)