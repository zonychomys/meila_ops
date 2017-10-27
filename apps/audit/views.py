# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import os
import signal

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponse, HttpResponseNotFound,
    HttpResponseRedirect, JsonResponse,
)
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.timezone import localtime, utc
from django.views import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from logic.db.meila_ops.models import Audit


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class AuditExecuteListView(View):

    def get(self, request, status):
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        if status == 'online':
            audits = Audit.objects.filter(is_active=True)
            is_active = True
        elif status == 'history':
            audits = Audit.objects.filter(is_active=False)
            is_active = False
        else:
            return HttpResponseNotFound()
        p = Paginator(audits, 10, request=request)
        audits = p.page(page)
        context = dict(
            audits=audits,
            is_active=is_active,
        )
        return render(request, 'audit/audit_execute_list.html', context)


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class AuditExecuteDetailView(View):

    def get(self, request, pk):
        if request.is_ajax():
            command_history = []
            audit = Audit.objects.get(id=pk)
            for i in audit.auditexecute_set.all():
                command_history.append({
                    'time': localtime(i.time).strftime('%Y-%m-%d %H:%M:%S'),
                    'command': i.command,
                })
            return JsonResponse(data=command_history, safe=False)
        else:
            return HttpResponseNotFound()


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class AuditExecuteDeleteView(View):

    def post(self, request, pk):
        audit = Audit.objects.get(id=pk)
        audit.delete()
        return HttpResponse('删除成功')


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class AuditExecuteKillView(View):

    def post(self, request, pk):
        audit = Audit.objects.get(id=pk)
        os.kill(audit.pid, signal.SIGTERM)
        audit.is_active = False
        audit.end_time = datetime.datetime.utcnow().replace(tzinfo=utc)
        audit.save()
        return HttpResponse()
