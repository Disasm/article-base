from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pdfbase.views.home', name='home'),
    # url(r'^pdfbase/', include('pdfbase.foo.urls')),
    (r'^$', RedirectView.as_view(url='/items/')),
    url(r'^new/$', 'web.views.item_add'),
    url(r'^items/$', 'web.views.item_list'),
    url(r'^item/(?P<id>\d+)/$', 'web.views.item_show'),
    url(r'^item/(?P<id>\d+)/edit/$', 'web.views.item_edit'),
    url(r'^item/(?P<id>\d+)/delete/$', 'web.views.item_delete'),
    url(r'^tags/$', 'web.views.get_tags'),
    url(r'^tag/(?P<tags>[\d,]+)/$', 'web.views.get_tag_items'),

    ('^accounts/', include('django.contrib.auth.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
