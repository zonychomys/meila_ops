from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^account/$', views.AccountListView.as_view(), name='AccountList'),
    url(r'^account/create/$', views.AccountCreateView.as_view(), name='AccountCreate'),
    url(r'^account/delete/$', views.AccountDeleteView.as_view(), name='AccountMultiDelete'),
    url(r'^account/(?P<pk>\d+)/update/$', views.AccountUpdateView.as_view(), name='AccountUpdate'),
    url(r'^account/(?P<pk>\d+)/delete/$', views.AccountDeleteView.as_view(), name='AccountDelete'),

    url(r'^rule/$', views.PermissionListView.as_view(), name='PermissionList'),
    url(r'^rule/create/$', views.PermissionCreateView.as_view(), name='PermissionCreate'),
    url(r'^rule/delete/$', views.PermissionDeleteView.as_view(), name='PermissionMultiDelete'),
    url(r'^rule/(?P<pk>\d+)/update/$', views.PermissionUpdateView.as_view(), name='PermissionUpdate'),
    url(r'^rule/(?P<pk>\d+)/delete/$', views.PermissionDeleteView.as_view(), name='PermissionDelete'),
]
