from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
import viewsets

router = DefaultRouter()
router.register(r'mints', viewsets.MintViewSet)
router.register(r'countries', viewsets.CountryViewSet)
router.register(r'currencies', viewsets.CurrencyViewSet)
router.register(r'collections', viewsets.CollectionViewSet)

urlpatterns = patterns(
    'coins.views',
    url(r'^', include(router.urls))
)
