from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'hubvan.apps.hubvan.views.index', name='index'),
    # url(r'^hubvan/', include('hubvan.foo.urls')),
    url(r'^oauth_callback$', 'hubvan.apps.hubvan.views.oauth_callback', name='oauth_callback'),
    url(r'^(?P<user>\w+)$', 'hubvan.apps.hubvan.views.user', name='userpage'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
