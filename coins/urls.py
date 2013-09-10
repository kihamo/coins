from django.conf.urls import patterns, url
from views import MintList

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
    url(r'^mints/$', MintList.as_view()),
)