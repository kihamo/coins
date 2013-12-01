from django.conf import settings
from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
import viewsets
import views

router = DefaultRouter()
router.register(r'mints', viewsets.MintViewSet)
router.register(r'countries', viewsets.CountryViewSet)
router.register(r'currencies', viewsets.CurrencyViewSet)
router.register(r'collections', viewsets.CollectionViewSet)

urlpatterns = patterns(
    'coins.views',
    url(r'^', include(router.urls)),
    url(r'^user/token', views.DeviceTokenView.as_view()),
    # http://stackoverflow.com/questions/14567586/token-authentication-for-restful-api-should-the-token-be-periodically-changed
    url(r'^user/login', obtain_auth_token)
)

if ('rest_framework.authentication.SessionAuthentication'
    in settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] and
    'rest_framework.renderers.BrowsableAPIRenderer'
        in settings.REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES']):
    urlpatterns += patterns(
        '',
        url(r'^auth/', include('rest_framework.urls', namespace='rest_framework'))
    )
