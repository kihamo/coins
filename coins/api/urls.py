from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
import viewsets

router = DefaultRouter()
router.register(r'mints', viewsets.MintViewSet)
router.register(r'countries', viewsets.CountryViewSet)
router.register(r'currencies', viewsets.CurrencyViewSet)
router.register(r'collections', viewsets.CollectionViewSet)
router.register(r'user/token', viewsets.DeviceTokenViewSet)

urlpatterns = patterns(
    'coins.views',
    url(r'^', include(router.urls)),
    # http://stackoverflow.com/questions/14567586/token-authentication-for-restful-api-should-the-token-be-periodically-changed
    url(r'^user/login', obtain_auth_token)
)
