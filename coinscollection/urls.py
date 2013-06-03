from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^cp/doc/', include('django.contrib.admindocs.urls')),
    url(r'^cp_tools/', include('admin_tools.urls')),
    (r'^cp/', include(admin.site.urls)),

    url(r'^coins/', include('coins.urls')),

) + staticfiles_urlpatterns()
