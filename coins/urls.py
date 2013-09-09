from django.conf.urls import patterns, url

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
)