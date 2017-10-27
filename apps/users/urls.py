from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^group/$', views.UserGroupListView.as_view(), name='UserGroupList'),
    url(r'^group/create/$', views.UserGroupCreateView.as_view(), name='UserGroupCreate'),
    url(r'^group/delete/$', views.UserGroupDeleteView.as_view(), name='UserGroupMultiDelete'),
    url(r'^group/(?P<pk>\d+)/update/$', views.UserGroupUpdateView.as_view(), name='UserGroupUpdate'),
    url(r'^group/(?P<pk>\d+)/delete/$', views.UserGroupDeleteView.as_view(), name='UserGroupDelete'),

    url(r'^user/$', views.UserListView.as_view(), name='UserList'),
    url(r'^user/create/$', views.UserCreateView.as_view(), name='UserCreate'),
    url(r'^user/delete/$', views.UserDeleteView.as_view(), name='UserMultiDelete'),
    url(r'^user/(?P<pk>\d+)/update/$', views.UserUpdateView.as_view(), name='UserUpdate'),
    url(r'^user/(?P<pk>\d+)/delete/$', views.UserDeleteView.as_view(), name='UserDelete'),
    url(r'^user/(?P<pk>\d+)/notify/$', views.UserEmailNotifyView.as_view(), name='UserEmailNotify'),
]
