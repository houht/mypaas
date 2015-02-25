from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from app import views


urlpatterns = patterns('',
    
    
    url(r'^$', views.AppList.as_view()),
    url(r'^(?P<appId>[0-9a-z]+)/$', views.AppDetail.as_view()),
    
    url(r'^(?P<appId>[0-9a-z]+)/instance/$', views.InstanceList.as_view()),
    url(r'^(?P<appId>[0-9a-z]+)/instance/(?P<instanceId>[0-9a-z]+)/$', views.InstanceDetail.as_view()),
    
    
    
)

urlpatterns = format_suffix_patterns(urlpatterns)