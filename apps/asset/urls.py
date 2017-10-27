from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^group/$', views.AssetGroupListView.as_view(), name='AssetGroupList'),
    url(r'^group/create/$', views.AssetGroupCreateView.as_view(), name='AssetGroupCreate'),
    url(r'^group/delete/$', views.AssetGroupDeleteView.as_view(), name='AssetGroupMultiDelete'),
    url(r'^group/(?P<pk>\d+)/update/$', views.AssetGroupUpdateView.as_view(), name='AssetGroupUpdate'),
    url(r'^group/(?P<pk>\d+)/delete/$', views.AssetGroupDeleteView.as_view(), name='AssetGroupDelete'),

    url(r'^server/$', views.AssetServerListView.as_view(), name='AssetServerList'),
    url(r'^server/create/$', views.AssetServerCreateView.as_view(), name='AssetServerCreate'),
    url(r'^server/delete/$', views.AssetServerDeleteView.as_view(), name='AssetServerMultiDelete'),
    url(r'^server/(?P<pk>\d+)/update/$', views.AssetServerUpdateView.as_view(), name='AssetServerUpdate'),
    url(r'^server/(?P<pk>\d+)/delete/$', views.AssetServerDeleteView.as_view(), name='AssetServerDelete'),

    url(r'^asset/search/$', views.AssetAjaxSearchView.as_view(), name='AssetAjaxSearch'),
]
