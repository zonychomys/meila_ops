from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='Index'),
    url(r'^login/$', views.LoginView.as_view(), name='Login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='Logout'),
    url(r'^password/new/$', views.SetPasswordView.as_view(), name='SetPassword'),
    url(r'^initialize/$', views.InitializeView.as_view(), name='Initialize'),
]
