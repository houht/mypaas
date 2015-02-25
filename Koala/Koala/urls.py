from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Koala.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    #url(r'^admin/', include(admin.site.urls)),
 
    url(r'^auth/', include('rest_framework.urls',
                                namespace='rest_framework')), 
                                
    url(r'^v1/app/', include('app.urls')),
    url(r'^v1/vm/', include('vm.urls')),
    

)
