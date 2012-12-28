from django.conf.urls import patterns, url

import views

urlpatterns = patterns('',
    url(
        r'^image\/(.+?)(?:[.](\d+)x(\d+))?(?:[.](jpg|jpeg|png|gif))?$',
        views.image
    ),
    url(
        r'^barcode\/(\d+)(?:[.](qr|code128))?(?:[.](jpg|jpeg|png|gif))?$',
        views.barcode
    ),
    url(
        r'^box\/(\d+)(?:[.](html|pdf))?$',
        views.box
    ),
)