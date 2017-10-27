# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from logic.comm_def import AssetType, AssetStatusType
from logic.db.meila_ops.models import Asset, AssetGroup


class AssetGroupCreateForm(forms.Form):
    name = forms.CharField(
        required=True,
        max_length=20,
        error_messages={
            'required': '资产组名不能为空',
            'max_length': '请将资产组名限制在20个字符以内',
        },
    )
    desc = forms.CharField(
        required=False,
        max_length=50,
        error_messages={
            'max_length': '请将描述信息限制在50个字符以内',
        },
    )
    type = forms.ChoiceField(
        required=True,
        choices=AssetType.attrs.items(),
        error_messages={
            'invalid_choice': '非法的资产类型',
            'required': '请选择资产类型',
        },
    )
    assets = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Asset.objects.all(),
    )


class AssetGroupUpdateForm(forms.Form):
    name = forms.CharField(
        required=True,
        max_length=20,
        error_messages={
            'required': '资产组名不能为空',
            'max_length': '请将资产组名限制在20个字符以内',
        },
    )
    desc = forms.CharField(
        required=False,
        max_length=50,
        error_messages={
            'max_length': '请将描述信息限制在50个字符以内',
        },
    )
    type = forms.ChoiceField(
        required=True,
        choices=AssetType.attrs.items(),
        error_messages={
            'invalid_choice': '非法的资产类型',
            'required': '请选择资产类型',
        },
    )
    assets = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Asset.objects.all(),
    )


class AssetServerCreateForm(forms.Form):
    hostname = forms.CharField(
        required=True,
        max_length=20,
        error_messages={
            'required': '主机名不能为空',
            'max_length': '请将主机名限制在20个字符以内',
        },
    )
    ip = forms.GenericIPAddressField(
        required=True,
        error_messages={
            'invalid': '非法的IP地址格式',
            'required': 'IP地址不能为空',
        },
    )
    port = forms.IntegerField(
        required=True,
        min_value=1,
        max_value=65535,
        error_messages={
            'invalid': '非法的端口号范围(0-65535)',
            'required': '请输入SSH远程连接端口',
        },
    )
    status = forms.ChoiceField(
        required=True,
        choices = AssetStatusType.attrs.items(),
        error_messages={
            'invalid_choice': '非法的资产状态',
            'required': '资产状态不能为空',
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
    groups = forms.ModelMultipleChoiceField(
        required=False,
        queryset=AssetGroup.objects.all(),
    )


class AssetServerUpdateForm(forms.Form):
    hostname = forms.CharField(
        required=True,
        max_length=20,
        error_messages={
            'required': '主机名不能为空',
            'max_length': '请将主机名限制在20个字符以内',
        },
    )
    ip = forms.GenericIPAddressField(
        required=True,
        error_messages={
            'invalid': '非法的IP地址格式',
            'required': 'IP地址不能为空',
        },
    )
    port = forms.IntegerField(
        required=True,
        min_value=1,
        max_value=65535,
        error_messages={
            'invalid': '非法的端口号范围(0-65535)',
            'required': '请输入SSH远程连接端口',
        },
    )
    status = forms.ChoiceField(
        required=True,
        choices = AssetStatusType.attrs.items(),
        error_messages={
            'invalid_choice': '非法的资产状态',
            'required': '资产状态不能为空',
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
    groups = forms.ModelMultipleChoiceField(
        required=False,
        queryset=AssetGroup.objects.all(),
    )
