#/usr/bin/env python
#coding=utf8
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'helloemsg.views.home', name='home'),
    # url(r'^helloemsg/', include('helloemsg.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
	('^fileserver/token/$','service.views.token'),
	('^fileserver/upload/$','service.views.upload'),
    ('^fileserver/get/(.+)/$','service.views.getFile'),
    ('^fileserver/del/$','service.views.delFile'),
    ('^fileserver/info/(.+)/$','service.views.infoFile'),
    ('^fileserver/doc2html/(.+)/$','service.views.doc2html'),
    # 重新加载配置 
	('^callback/reload_cfg/$','service.views.callback_reload_cfg'),
)
