from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from vm import views


urlpatterns = patterns('',

    url(r'^$', views.VmList.as_view()),
    url(r'^(?P<vmId>[0-9a-z]+)/$', views.VmDetail.as_view()),
    url(r'^(?P<vmId>[0-9a-z]+)/net/$', views.VmNetList.as_view()),
    url(r'^(?P<vmId>[0-9a-z]+)/disk/$', views.VmDiskList.as_view()),
    
)

urlpatterns = format_suffix_patterns(urlpatterns)