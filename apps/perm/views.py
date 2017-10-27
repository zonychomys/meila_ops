# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from logic.comm_def import AssetType
from logic.db.meila_ops.models import (
    User, UserGroup, AssetGroup,
    AssetServer, Account, Permission,
)
from .forms import (
    AccountCreateForm, AccountUpdateForm,
    PermissionCreateForm, PermissionUpdateForm,
)


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class AccountListView(View):

    def get(self, request):
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        accounts = Account.objects.all()
        p = Paginator(accounts, 10, request=request)
        accounts = p.page(page)
        context = dict(
            accounts=accounts,
        )
        return render(request, 'perm/account_list.html', context)


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class AccountCreateView(View):

    def get(self, request):
        servers = AssetServer.objects.all()
        context = dict(
            servers=servers,
        )
        return render(request, 'perm/account_create.html', context)

    def post(self, request):
        form = AccountCreateForm(request.POST)
        if form.is_valid():
            servers = form.cleaned_data.get('servers')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            desc = form.cleaned_data.get('desc')
            try:
                account = Account.objects.create(
                    username=username,
                    password=password,
                    desc=desc,
                )
                account.refresh_from_db()
            except Exception, e:
                servers = AssetServer.objects.all()
                context = dict(
                    error_msg=e,
                    servers=servers,
                )
                return render(request, 'perm/account_create.html', context)
            else:
                account.servers.add(*servers)
                return HttpResponseRedirect(reverse('perm:AccountList'))
        else:
            servers = AssetServer.objects.all()
            context = dict(
                form=form,
                servers=servers,
            )
            return render(request, 'perm/account_create.html', context)


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class AccountUpdateView(View):

    def get(self, request, pk):
        account = Account.objects.get(id=pk)
        servers = AssetServer.objects.exclude(id__in=account.servers.all())
        context = dict(
            account=account,
            servers=servers,
        )
        return render(request, 'perm/account_update.html', context)

    def post(self, request, pk):
        form = AccountUpdateForm(request.POST)
        if form.is_valid():
            servers = form.cleaned_data.get('servers')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            desc = form.cleaned_data.get('desc')
            try:
                account = Account.objects.get(id=pk)
                account.username = username
                account.password = password
                account.desc = desc
                account.save()
                account.refresh_from_db()
            except Exception, e:
                account = Account.objects.get(id=pk)
                servers = AssetServer.objects.exclude(id__in=account.servers.all())
                context = dict(
                    error_msg=e,
                    account=account,
                    servers=servers,
                )
                return render(request, 'perm/account_update.html', context)
            else:
                account.servers.clear()
                account.servers.add(*servers)
                return HttpResponseRedirect(reverse('perm:AccountList'))
        else:
            account = Account.objects.get(id=pk)
            servers = AssetServer.objects.exclude(id__in=account.servers.all())
            context = dict(
                form=form,
                account=account,
                servers=servers,
            )
            return render(request, 'perm/account_update.html', context)


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class AccountDeleteView(View):

    def post(self, request, pk):
        account = Account.objects.get(id=pk)
        account.delete()
        return HttpResponse('删除成功')

    def delete(self, request):
        accounts_id = json.loads(request.body).get('data_items')
        accounts = Account.objects.filter(id__in=accounts_id)
        accounts.delete()
        return HttpResponse('删除成功')


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class PermissionListView(View):

    def get(self, request):
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        permissions = Permission.objects.all()
        p = Paginator(permissions, 10, request=request)
        permissions = p.page(page)
        context = dict(
            permissions=permissions,
        )
        return render(request, 'perm/permission_list.html', context)


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class PermissionCreateView(View):

    def get(self, request):
        users = User.objects.all()
        user_groups = UserGroup.objects.all()
        assets = AssetServer.objects.all()
        asset_groups = AssetGroup.objects.filter(type=AssetType.server)
        context = dict(
            users=users,
            user_groups=user_groups,
            assets=assets,
            asset_groups=asset_groups,
        )
        return render(request, 'perm/permission_create.html', context)

    def post(self, request):
        form = PermissionCreateForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            users = form.cleaned_data.get('users')
            user_groups = form.cleaned_data.get('user_groups')
            assets = form.cleaned_data.get('assets')
            asset_groups = form.cleaned_data.get('asset_groups')
            desc = form.cleaned_data.get('desc')
            try:
                permission = Permission.objects.create(
                    name=name,
                    desc=desc,
                )
                permission.refresh_from_db()
            except IntegrityError:
                error_msg = '该授权规则名称已存在'
                users = User.objects.all()
                user_groups = UserGroup.objects.all()
                assets = AssetServer.objects.all()
                asset_groups = AssetGroup.objects.filter(type=AssetType.server)
                context = dict(
                    error_msg=error_msg,
                    users=users,
                    user_groups=user_groups,
                    assets=assets,
                    asset_groups=asset_groups,
                )
                return render(request, 'perm/permission_create.html', context)
            else:
                permission.users.add(*users)
                permission.user_groups.add(*user_groups)
                permission.assets.add(*assets)
                permission.asset_groups.add(*asset_groups)
                return HttpResponseRedirect(reverse('perm:PermissionList'))
        else:
            users = User.objects.all()
            user_groups = UserGroup.objects.all()
            assets = AssetServer.objects.all()
            asset_groups = AssetGroup.objects.filter(type=AssetType.server)
            context = dict(
                form=form,
                users=users,
                user_groups=user_groups,
                assets=assets,
                asset_groups=asset_groups,
            )
            return render(request, 'perm/permission_create.html', context)


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class PermissionUpdateView(View):

    def get(self, request, pk):
        permission = Permission.objects.get(id=pk)
        users = User.objects.exclude(id__in=permission.users.all())
        user_groups = UserGroup.objects.exclude(id__in=permission.user_groups.all())
        assets = AssetServer.objects.exclude(id__in=permission.assets.all())
        asset_groups = AssetGroup.objects.exclude(
            Q(id__in=permission.asset_groups.all()) &
            Q(type=AssetType.server)
        )
        context = dict(
            permission=permission,
            users=users,
            user_groups=user_groups,
            assets=assets,
            asset_groups=asset_groups,
        )
        return render(request, 'perm/permission_update.html', context)

    def post(self, request, pk):
        form = PermissionUpdateForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            users = form.cleaned_data.get('users')
            user_groups = form.cleaned_data.get('user_groups')
            assets = form.cleaned_data.get('assets')
            asset_groups = form.cleaned_data.get('asset_groups')
            desc = form.cleaned_data.get('desc')
            try:
                permission = Permission.objects.get(id=pk)
                permission.name = name
                permission.desc = desc
                permission.save()
                permission.refresh_from_db()
            except IntegrityError:
                error_msg = '该授权规则名称已存在'
                permission = Permission.objects.get(id=pk)
                users = User.objects.exclude(id__in=permission.users.all())
                user_groups = UserGroup.objects.exclude(id__in=permission.user_groups.all())
                assets = AssetServer.objects.exclude(id__in=permission.assets.all())
                asset_groups = AssetGroup.objects.exclude(
                    Q(id__in=permission.asset_groups.all()) &
                    Q(type=AssetType.server)
                )
                context = dict(
                    error_msg=error_msg,
                    permission=permission,
                    users=users,
                    user_groups=user_groups,
                    assets=assets,
                    asset_groups=asset_groups,
                )
                return render(request, 'perm/permission_update.html', context)
            else:
                permission.users.clear()
                permission.users.add(*users)
                permission.user_groups.clear()
                permission.user_groups.add(*user_groups)
                permission.assets.clear()
                permission.assets.add(*assets)
                permission.asset_groups.clear()
                permission.asset_groups.add(*asset_groups)
                return HttpResponseRedirect(reverse('perm:PermissionList'))
        else:
            permission = Permission.objects.get(id=pk)
            users = User.objects.exclude(id__in=permission.users.all())
            user_groups = UserGroup.objects.exclude(id__in=permission.user_groups.all())
            assets = AssetServer.objects.exclude(id__in=permission.assets.all())
            asset_groups = AssetGroup.objects.exclude(
                Q(id__in=permission.asset_groups.all()) &
                Q(type=AssetType.server)
            )
            context = dict(
                form=form,
                permission=permission,
                users=users,
                user_groups=user_groups,
                assets=assets,
                asset_groups=asset_groups,
            )
            return render(request, 'perm/permission_update.html', context)


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class PermissionDeleteView(View):

    def post(self, request, pk):
        permission = Permission.objects.get(id=pk)
        permission.delete()
        return HttpResponse('删除成功')

    def delete(self, request):
        permissions_id = json.loads(request.body).get('data_items')
        permissions = Permission.objects.filter(id__in=permissions_id)
        permissions.delete()
        return HttpResponse('删除成功')
