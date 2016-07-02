from django.conf.urls import include, url

from djcelery.views import apply


urlpatterns = [
    # Example:
    # (r'^tests/', include('tests.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/(.*)', admin.site.root),
    url(r'^apply/(?P<task_name>.+?)/', apply, name='celery-apply'),
    url(r'^celery/', include('djcelery.urls')),

]
