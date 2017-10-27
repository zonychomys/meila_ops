# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import (
    HttpResponse, HttpResponseNotFound,
    HttpResponseRedirect, JsonResponse,
)
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from logic.comm_def import AssetType, AssetStatusType
from logic.db.meila_ops.models import (
    Asset, AssetGroup, AssetServer, AdminAccount
)
from .forms import (
    AssetGroupCreateForm, AssetGroupUpdateForm,
    AssetServerCreateForm, AssetServerUpdateForm,
)


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class AssetGroupListView(View):

    def get(self, request):
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        groups = AssetGroup.objects.all()
        p = Paginator(groups, 10, request=request)
        groups = p.page(page)
        context = dict(
            groups=groups,
        )
        return render(request, 'asset/asset_group_list.html', context)


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class AssetGroupCreateView(View):

    def get(self, request):
        asset_types = AssetType.attrs
        context = dict(
            asset_types=asset_types,
        )
        return render(request, 'asset/asset_group_create.html', context)

    def post(self, request):
        form = AssetGroupCreateForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            type = form.cleaned_data.get('type')
            desc = form.cleaned_data.get('desc')
            assets = form.cleaned_data.get('assets')
            try:
                group = AssetGroup.objects.create(name=name, type=type, desc=desc)
                group.refresh_from_db()
            except IntegrityError:
                error_msg = '该名称已被占用'
                asset_types = AssetType.attrs
                context = dict(
                    error_msg=error_msg,
                    asset_types=asset_types,
                )
                return render(request, 'asset/asset_group_create.html', context)
            else:
                group.asset_set.add(*assets)
                return HttpResponseRedirect(reverse('asset:AssetGroupList'))
        else:
            asset_types = AssetType.attrs
            context = dict(
                form=form,
                asset_types=asset_types,
            )
            return render(request, 'asset/asset_group_create.html', context)


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class AssetGroupUpdateView(View):

    def get(self, request, pk):
        group = AssetGroup.objects.get(id=pk)
        assets = Asset.objects.filter(type=group.type).exclude(groups=group)
        context = dict(
            group=group,
            assets=assets,
        )
        return render(request, 'asset/asset_group_update.html', context)

    def post(self, request, pk):
        form = AssetGroupUpdateForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            desc = form.cleaned_data.get('desc')
            assets = form.cleaned_data.get('assets')
            try:
                group = AssetGroup.objects.get(id=pk)
                group.name = name
                group.desc = desc
                group.save()
                group.refresh_from_db()
            except IntegrityError:
                error_msg = '该名称已被占用'
                group = AssetGroup.objects.get(id=pk)
                assets = Asset.objects.filter(type=group.type).exclude(groups=group)
                context = dict(
                    error_msg=error_msg,
                    group=group,
                    assets=assets,
                )
                return render(request, 'asset/asset_group_update.html', context)
            else:
                group.asset_set.clear()
                group.asset_set.add(*assets)
                return HttpResponseRedirect(reverse('asset:AssetGroupList'))
        else:
            group = AssetGroup.objects.get(id=pk)
            assets = Asset.objects.filter(type=group.type).exclude(groups=group)
            context = dict(
                form=form,
                group=group,
                assets=assets,
            )
            return render(request, 'asset/asset_group_update.html', context)


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class AssetGroupDeleteView(View):

    def post(self, request, pk):
        group = AssetGroup.objects.get(id=pk)
        group.delete()
        return HttpResponse('删除成功')

    def delete(self, request):
        groups_id = json.loads(request.body).get('data_items')
        groups = AssetGroup.objects.filter(id__in=groups_id)
        groups.delete()
        return HttpResponse('删除成功')


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class AssetServerListView(View):

    def get(self, request):
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        servers = AssetServer.objects.all()
        p = Paginator(servers, 10, request=request)
        servers = p.page(page)
        context = dict(
            servers=servers,
        )
        return render(request, 'asset/asset_server_list.html', context)


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class AssetServerCreateView(View):

    def get(self, request):
        groups = AssetGroup.objects.all()
        status_types = AssetStatusType.attrs
        context = dict(
            groups=groups,
            status_types=status_types,
        )
        return render(request, 'asset/asset_server_create.html', context)

    def post(self, request):
        form = AssetServerCreateForm(request.POST)
        if form.is_valid():
            hostname = form.cleaned_data.get('hostname')
            ip = form.cleaned_data.get('ip')
            port = form.cleaned_data.get('port')
            status = form.cleaned_data.get('status')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            groups = form.cleaned_data.get('groups')
            try:
                asset = Asset.objects.create(
                    type=AssetType.server,
                    status=status,
                )
                asset.refresh_from_db()
                server = AssetServer.objects.create(
                    hostname=hostname,
                    ip=ip,
                    port=port,
                    asset=asset,
                )
                server.refresh_from_db()
                account = AdminAccount.objects.create(
                    username=username,
                    password=password,
                    server = server,
                )
                account.refresh_from_db()
            except IntegrityError:
                asset.delete()
                error_msg = '该主机名已存在'
                groups = AssetGroup.objects.all()
                status_types = AssetStatusType.attrs
                context = dict(
                    error_msg=error_msg,
                    groups=groups,
                    status_types=status_types,
                )
                return render(request, 'asset/asset_server_create.html', context)
            else:
                asset.groups.add(*groups)
                return HttpResponseRedirect(reverse('asset:AssetServerList'))
        else:
            groups = AssetGroup.objects.all()
            status_types = AssetStatusType.attrs
            context = dict(
                form=form,
                groups=groups,
                status_types=status_types,
            )
            return render(request, 'asset/asset_server_create.html', context)


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class AssetServerUpdateView(View):

    def get(self, request, pk):
        server = AssetServer.objects.get(id=pk)
        groups = AssetGroup.objects.exclude(asset=server.asset)
        status_types = AssetStatusType.attrs
        context = dict(
            server=server,
            groups=groups,
            status_types=status_types,
        )
        return render(request, 'asset/asset_server_update.html', context)

    def post(self, request, pk):
        form = AssetServerUpdateForm(request.POST)
        if form.is_valid():
            hostname = form.cleaned_data.get('hostname')
            ip = form.cleaned_data.get('ip')
            port = form.cleaned_data.get('port')
            status = form.cleaned_data.get('status')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            groups = form.cleaned_data.get('groups')
            try:
                server = AssetServer.objects.get(id=pk)
                server.hostname = hostname
                server.ip = ip
                server.port = port
                server.save()
                server.refresh_from_db()
            except IntegrityError:
                error_msg = '该主机名已存在'
                server = AssetServer.objects.get(id=pk)
                groups = AssetGroup.objects.exclude(asset=server.asset)
                status_types = AssetStatusType.attrs
                context = dict(
                    error_msg=error_msg,
                    server=server,
                    groups=groups,
                    status_types=status_types,
                )
                return render(request, 'asset/asset_server_update.html', context)
            else:
                server.adminaccount.username = username
                server.adminaccount.password = password
                server.adminaccount.save()
                server.adminaccount.refresh_from_db()
                server.asset.status = status
                server.asset.save()
                server.asset.refresh_from_db()
                server.asset.groups.clear()
                server.asset.groups.add(*groups)
                return HttpResponseRedirect(reverse('asset:AssetServerList'))
        else:
            server = AssetServer.objects.get(id=pk)
            groups = AssetGroup.objects.exclude(asset=server.asset)
            status_types = AssetStatusType.attrs
            context = dict(
                form=form,
                server=server,
                groups=groups,
                status_types=status_types,
            )
            return render(request, 'asset/asset_server_update.html', context)


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class AssetServerDeleteView(View):

    def post(self, request, pk):
        server = AssetServer.objects.get(id=pk)
        server.asset.delete()
        return HttpResponse('删除成功')

    def delete(self, request):
        servers_id = json.loads(request.body).get('data_items')
        servers = Asset.objects.filter(assetserver__in=servers_id)
        servers.delete()
        return HttpResponse('删除成功')


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class AssetAjaxSearchView(View):

    def get(self, request):
        if request.is_ajax():
            data = []
            asset_type = int(request.GET.get('type'))
            assets = Asset.objects.filter(type=asset_type)
            for asset in assets:
                data.append(dict(pk=asset.id, label=asset.get_asset_label()))
            return JsonResponse(data=data, safe=False)
        else:
            return HttpResponseNotFound()
