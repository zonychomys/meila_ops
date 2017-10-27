# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from logic.comm_def import AssetType
from logic.db.meila_ops.models import (
    User, UserGroup, AssetGroup, AssetServer, Account,
)


class AccountCreateForm(forms.Form):
    servers = forms.ModelMultipleChoiceField(
        required=True,
        queryset=AssetServer.objects.all(),
        error_messages={
            'required': '请至少选择一台服务器',
        },
    )
    username = forms.CharField(
        required=True,
        max_length=20,
        error_messages={
            'required': '账户名称不能为空',
            'max_length': '请将账户名称限制在20个字符以内',
        },
    )
    password = forms.CharField(
        required=True,
        min_length=8,
        max_length=30,
        error_messages={
            'required': '账户密码不能为空',
            'min_length': '账户密码长度应大于8个字符',
            'max_length': '账户密码长度应限制在30个字符以内',
        },
    )
    desc = forms.CharField(
        required=False,
        max_length=50,
        error_messages={
            'max_length': '请将描述信息限制在50个字符以内',
        },
    )

    def clean_username(self):
        servers = self.cleaned_data.get('servers')
        username = self.cleaned_data.get('username')
        if username in servers.values_list('account__username', flat=True):
            hosts_invalid = []
            for server in servers:
                for account in server.account_set.all():
                    if account.username == username:
                        hosts_invalid.append(server.hostname)
            msg = '目标机器{hosts}已存在系统账户{account}'.format(
                hosts=','.join(hosts_invalid),
                account=username,
            )
            raise forms.ValidationError(msg)
        else:
            return username


class AccountUpdateForm(forms.Form):
    servers = forms.ModelMultipleChoiceField(
        required=True,
        queryset=AssetServer.objects.all(),
        error_messages={
            'required': '请至少选择一台服务器',
        },
    )
    username = forms.CharField(
        required=True,
        max_length=20,
        error_messages={
            'required': '账户名称不能为空',
            'max_length': '请将账户名称限制在20个字符以内',
        },
    )
    password = forms.CharField(
        required=True,
        min_length=8,
        max_length=30,
        error_messages={
            'required': '账户密码不能为空',
            'min_length': '账户密码长度应大于8个字符',
            'max_length': '账户密码长度应限制在30个字符以内',
        },
    )
    desc = forms.CharField(
        required=False,
        max_length=50,
        error_messages={
            'max_length': '请将描述信息限制在50个字符以内',
        },
    )


class PermissionCreateForm(forms.Form):
    name = forms.CharField(
        required=True,
        max_length=20,
        error_messages={
            'required': '授权规则名称不能为空',
            'max_length': '请将授权规则名称限制在20个字符以内',
        },
    )
    users = forms.ModelMultipleChoiceField(
        required=False,
        queryset=User.objects.all(),
    )
    user_groups = forms.ModelMultipleChoiceField(
        required=False,
        queryset=UserGroup.objects.all(),
    )
    assets = forms.ModelMultipleChoiceField(
        required=False,
        queryset=AssetServer.objects.all(),
    )
    asset_groups = forms.ModelMultipleChoiceField(
        required=False,
        queryset=AssetGroup.objects.filter(type=AssetType.server),
    )
    desc = forms.CharField(
        required=False,
        max_length=50,
        error_messages={
            'max_length': '请将描述信息限制在50个字符以内',
        },
    )

    def clean(self):
        self.cleaned_data = super(PermissionCreateForm, self).clean()
        users = self.cleaned_data.get('users')
        user_groups = self.cleaned_data.get('user_groups')
        assets = self.cleaned_data.get('assets')
        asset_groups = self.cleaned_data.get('asset_groups')
        if not users and not user_groups:
            self.add_error('users', '请在用户或用户组中选择至少一项')
            self.add_error('user_groups', '')
        if not assets and not asset_groups:
            self.add_error('assets', '请在资产或资产组中选择至少一项')
            self.add_error('asset_groups', '')
        return self.cleaned_data


class PermissionUpdateForm(forms.Form):
    name = forms.CharField(
        required=True,
        max_length=20,
        error_messages={
            'required': '授权规则名称不能为空',
            'max_length': '请将授权规则名称限制在20个字符以内',
        },
    )
    users = forms.ModelMultipleChoiceField(
        required=False,
        queryset=User.objects.all(),
    )
    user_groups = forms.ModelMultipleChoiceField(
        required=False,
        queryset=UserGroup.objects.all(),
    )
    assets = forms.ModelMultipleChoiceField(
        required=False,
        queryset=AssetServer.objects.all(),
    )
    asset_groups = forms.ModelMultipleChoiceField(
        required=False,
        queryset=AssetGroup.objects.filter(type=AssetType.server),
    )
    desc = forms.CharField(
        required=False,
        max_length=50,
        error_messages={
            'max_length': '请将描述信息限制在50个字符以内',
        },
    )

    def clean(self):
        self.cleaned_data = super(PermissionUpdateForm, self).clean()
        users = self.cleaned_data.get('users')
        user_groups = self.cleaned_data.get('user_groups')
        assets = self.cleaned_data.get('assets')
        asset_groups = self.cleaned_data.get('asset_groups')
        if not users and not user_groups:
            self.add_error('users', '请在用户或用户组中选择至少一项')
            self.add_error('user_groups', '')
        if not assets and not asset_groups:
            self.add_error('assets', '请在资产或资产组中选择至少一项')
            self.add_error('asset_groups', '')
        return self.cleaned_data
