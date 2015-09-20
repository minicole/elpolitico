from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'elpolitico.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # get the current status of the system:
    url(r'^get_status/green', 'app.views.party_check', {'party': 'green'}),
    url(r'^get_status/conservative', 'app.views.party_check', {'party': 'conservative'}),
    url(r'^get_status/liberal', 'app.views.party_check', {'party': 'liberal'}),
    url(r'^get_status/libertarian', 'app.views.party_check', {'party': 'libertarian'}),

    url(r'^get_status/new_points', 'app.views.new_points_check'),

    url(r'^admin/', include(admin.site.urls)),
)
