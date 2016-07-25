from __future__ import absolute_import, unicode_literals

from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    url(
        r'^doc/',
        include('django.contrib.admindocs.urls')
    ),

    url(r'', include(admin.site.urls)),
]
