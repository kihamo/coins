from django.conf.urls import patterns, url

import views

urlpatterns = patterns('',
    url(
        r'^image\/(?P<filename>.+?)([.](?P<width>\d+)x(?P<height>\d+))?[.](?P<format>(jpg|jpeg|png|gif))$',
        views.image_view
    ),
    url(
        r'^barcode\/(?P<coin_id>\d+)([.](?P<barcode_format>(qr|code128)))?[.](?P<image_format>(jpg|jpeg|png|gif))$',
        views.barcode_view
    ),
)