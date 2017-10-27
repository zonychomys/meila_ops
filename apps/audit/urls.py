from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^execute/(?P<status>\w+)/$', views.AuditExecuteListView.as_view(), name='AuditExecuteList'),
    url(r'^execute/(?P<pk>\d+)/detail/$', views.AuditExecuteDetailView.as_view(), name='AuditExecuteDetail'),
    url(r'^execute/(?P<pk>\d+)/delete/$', views.AuditExecuteDeleteView.as_view(), name='AuditExecuteDelete'),
    url(r'^execute/(?P<pk>\d+)/kill/$', views.AuditExecuteKillView.as_view(), name='AuditExecuteKill'),
]
