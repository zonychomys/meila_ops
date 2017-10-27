# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
import json
import urllib
import urlparse

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.views import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from logic.ansible.runner import AnsibleRunner
from logic.comm_def import UserRoleType, UserStatusType
from logic.db.meila_ops.models import User, UserGroup
from .forms import (
    UserGroupCreateForm, UserGroupUpdateForm,
    UserCreateForm, UserUpdateForm,
)


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class UserGroupListView(View):

    def get(self, request):
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        groups = UserGroup.objects.only('name', 'desc')
        p = Paginator(groups, 10, request=request)
        groups = p.page(page)
        context = dict(
            groups=groups,
        )
        return render(request, 'users/user_group_list.html', context)


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class UserGroupCreateView(View):

    def get(self, request):
        users = User.objects.only('id', 'username')
        context = dict(
            users=users,
        )
        return render(request, 'users/user_group_create.html', context)

    def post(self, request):
        form = UserGroupCreateForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            desc = form.cleaned_data.get('desc')
            users = form.cleaned_data.get('users')
            try:
                group = UserGroup.objects.create(name=name, desc=desc)
                group.refresh_from_db()
            except IntegrityError:
                error_msg = '该名称已被占用'
                users = User.objects.only('id', 'username')
                context = dict(
                    error_msg=error_msg,
                    users=users,
                )
                return render(request, 'users/user_group_create.html', context)
            else:
                group.user_set.add(*users)
                return HttpResponseRedirect(reverse('user:UserGroupList'))
        else:
            users = User.objects.only('id', 'username')
            context = dict(
                users=users,
                form=form,
            )
            return render(request, 'users/user_group_create.html', context)


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class UserGroupUpdateView(View):

    def get(self, request, pk):
        group = UserGroup.objects.get(id=pk)
        users = User.objects.exclude(groups=group)
        context = dict(
            group=group,
            users=users,
        )
        return render(request, 'users/user_group_update.html', context)

    def post(self, request, pk):
        form = UserGroupUpdateForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            desc = form.cleaned_data.get('desc')
            users = form.cleaned_data.get('users')
            try:
                group = UserGroup.objects.get(id=pk)
                group.name = name
                group.desc = desc
                group.save()
                group.refresh_from_db()
            except IntegrityError:
                error_msg = '该名称已被占用'
                group = UserGroup.objects.get(id=pk)
                users = User.objects.exclude(groups=group)
                context = dict(
                    error_msg=error_msg,
                    group=group,
                    users=users,
                )
                return render(request, 'users/user_group_update.html', context)
            else:
                group.user_set.clear()
                group.user_set.add(*users)
                return HttpResponseRedirect(reverse('user:UserGroupList'))
        else:
            group = UserGroup.objects.get(id=pk)
            users = User.objects.exclude(groups=group)
            context = dict(
                group=group,
                users=users,
                form=form,
            )
            return render(request, 'users/user_group_update.html', context)


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class UserGroupDeleteView(View):

    def post(self, request, pk):
        UserGroup.objects.get(id=pk).delete()
        return HttpResponse('删除成功')

    def delete(self, request):
        groups_id = json.loads(request.body).get('data_items')
        groups = UserGroup.objects.filter(id__in=groups_id)
        groups.delete()
        return HttpResponse('删除成功')


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class UserListView(View):

    def get(self, request):
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        users = User.objects.only('username', 'email', 'role', 'is_active')
        p = Paginator(users, 10, request=request)
        users = p.page(page)
        context = dict(
            users=users,
        )
        return render(request, 'users/user_list.html', context)


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class UserCreateView(View):

    def get(self, request):
        groups = UserGroup.objects.only('id', 'name')
        role_types = UserRoleType.attrs
        status_types = UserStatusType.attrs
        context = dict(
            groups=groups,
            role_types=role_types,
            status_types=status_types,
        )
        return render(request, 'users/user_create.html', context)

    def post(self, request):
        form = UserCreateForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            is_active = form.cleaned_data.get('is_active')
            role = form.cleaned_data.get('role')
            groups = form.cleaned_data.get('groups')
            try:
                user = User.objects.create_user(
                    email=email,
                    username=username,
                    is_active=is_active,
                    role=role,
                )
            except IntegrityError:
                error_msg = '用户名或邮箱地址已存在'
                groups = UserGroup.objects.only('id', 'name')
                role_types = UserRoleType.attrs
                status_types = UserStatusType.attrs
                context = dict(
                    error_msg=error_msg,
                    groups=groups,
                    role_types=role_types,
                    status_types=status_types,
                )
                return render(request, 'users/user_create.html', context)
            else:
                user.groups.add(*groups)
                sign = hashlib.md5(email + settings.SECRET_KEY).hexdigest()
                url = urlparse.ParseResult(
                    scheme=request.scheme,
                    netloc=urlparse.urlparse(request.get_raw_uri()).netloc,
                    path=reverse(('core:SetPassword')),
                    params='',
                    query = urllib.urlencode({'email': email, 'sign': sign}),
                    fragment='',
                ).geturl()
                msg = EmailMultiAlternatives(
                    subject='邮件激活通知',
                    body=get_template('users/user_email_activate.html').render({'url': url}),
                    from_email=settings.EMAIL_HOST_USER,
                    to=[email,],
                )
                msg.content_subtype = 'html'
                msg.send(fail_silently=True)
                return HttpResponseRedirect(reverse('user:UserList'))
        else:
            groups = UserGroup.objects.only('id', 'name')
            role_types = UserRoleType.attrs
            status_types = UserStatusType.attrs
            context = dict(
                groups=groups,
                role_types=role_types,
                status_types=status_types,
                form=form,
            )
            return render(request, 'users/user_create.html', context)


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class UserUpdateView(View):

    def get(self, request, pk):
        user = User.objects.get(id=pk)
        groups = UserGroup.objects.exclude(user=user)
        role_types = UserRoleType.attrs
        status_types = UserStatusType.attrs
        context = dict(
            user=user,
            groups=groups,
            role_types=role_types,
            status_types=status_types,
        )
        return render(request, 'users/user_update.html', context)

    def post(self, request, pk):
        form = UserUpdateForm(request.POST)
        if form.is_valid():
            is_active = form.cleaned_data.get('is_active')
            role = form.cleaned_data.get('role')
            groups = form.cleaned_data.get('groups')
            try:
                user = User.objects.get(id=pk)
                user.is_active = is_active
                user.role = role
                user.save()
                user.refresh_from_db()
            except IntegrityError:
                error_msg = '用户名或邮箱地址已存在'
                user = User.objects.get(id=pk)
                groups = UserGroup.objects.exclude(user=user)
                role_types = UserRoleType.attrs
                status_types = UserStatusType.attrs
                context = dict(
                    error_msg=error_msg,
                    user=user,
                    groups=groups,
                    role_types=role_types,
                    status_types=status_types,
                )
                return render(request, 'users/user_update.html', context)
            else:
                user.groups.clear()
                user.groups.add(*groups)
                return HttpResponseRedirect(reverse('user:UserList'))
        else:
            user = User.objects.get(id=pk)
            groups = UserGroup.objects.exclude(user=user)
            role_types = UserRoleType.attrs
            status_types = UserStatusType.attrs
            context = dict(
                user=user,
                groups=groups,
                role_types=role_types,
                status_types=status_types,
                form=form,
            )
            return render(request, 'users/user_update.html', context)


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class UserDeleteView(View):

    def post(self, request, pk):
        user = User.objects.get(id=pk)
        runner = AnsibleRunner(
            module_name='user',
            module_args=dict(
                state='absent',
                name=user.username,
                remove='yes',
                force='yes',
            ),
            pattern='localhost',
        )
        host_ok, host_failed, host_unreachable = runner.run()
        user.delete()
        return HttpResponse('删除成功')

    def delete(self, request):
        users_id = json.loads(request.body).get('data_items')
        users = User.objects.filter(id__in=users_id)
        for user in users:
            runner = AnsibleRunner(
                module_name='user',
                module_args=dict(
                    state='absent',
                    name=user.username,
                    remove='yes',
                    force='yes',
                ),
                pattern='localhost',
            )
            host_ok, host_failed, host_unreachable = runner.run()
            user.delete()
        return HttpResponse('删除成功')


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class UserEmailNotifyView(View):

    def post(self, request, pk):
        user = User.objects.get(id=pk)
        sign = hashlib.md5(user.email + settings.SECRET_KEY).hexdigest()
        url = urlparse.ParseResult(
            scheme=request.scheme,
            netloc=urlparse.urlparse(request.get_raw_uri()).netloc,
            path=reverse(('core:SetPassword')),
            params='',
            query = urllib.urlencode({'email': user.email, 'sign': sign}),
            fragment='',
        ).geturl()
        msg = EmailMultiAlternatives(
            subject='邮件激活通知',
            body=get_template('users/user_email_activate.html').render({'url': url}),
            from_email=settings.EMAIL_HOST_USER,
            to=[user.email,],
        )
        msg.content_subtype = 'html'
        status = msg.send(fail_silently=True)
        response = '邮件发送成功' if status else '邮件发送失败, 请重试'
        return HttpResponse(response)
