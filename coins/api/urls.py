from django.conf import settings
from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from views import *

router = DefaultRouter()
router.register(r'coins/sets', CoinSetViewSet)
router.register(r'banknotes/sets', BanknoteSetViewSet)
'''
router.register(r'mints', viewsets.MintViewSet)
router.register(r'countries', viewsets.CountryViewSet)
router.register(r'currencies', viewsets.CurrencyViewSet)
router.register(r'collections', viewsets.CollectionViewSet)
'''

urlpatterns = patterns(
    'coins.views',
    url(r'^', include(router.urls)),
    url(r'^user/token', DeviceTokenView.as_view()),
    url(r'^user/login', AuthTokenView.as_view())
)

if ('rest_framework.authentication.SessionAuthentication'
    in settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] and
    'rest_framework.renderers.BrowsableAPIRenderer'
        in settings.REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES']):
    urlpatterns += patterns(
        '',
        url(r'^auth/', include(
            'rest_framework.urls',
            namespace='rest_framework'))
    )
