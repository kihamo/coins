from django.conf.urls import patterns, include, url
from django.conf.urls.static import static

from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',

       (r'^cp/', include(admin.site.urls)),
    url(r'^cp_tools/', include('admin_tools.urls')),
    url(r'^coins/', include('coins.urls')),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
