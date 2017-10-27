# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms

from logic.comm_def import UserStatusType, UserRoleType
from logic.db.meila_ops.models import User, UserGroup


class UserGroupCreateForm(forms.Form):
    name = forms.CharField(
        required=True,
        max_length=20,
        error_messages={
            'required': '用户组名不能为空',
            'max_length': '请将用户组名限制在20个字符以内',
        },
    )
    desc = forms.CharField(
        required=False,
        max_length=50,
        error_messages={
            'max_length': '请将描述信息限制在50个字符以内',
        },
    )
    users = forms.ModelMultipleChoiceField(
        required=False,
        queryset=User.objects.all(),
    )


class UserGroupUpdateForm(forms.Form):
    name = forms.CharField(
        required=True,
        max_length=20,
        error_messages={
            'required': '用户组名不能为空',
            'max_length': '请将用户组名限制在20个字符以内',
        },
    )
    desc = forms.CharField(
        required=False,
        max_length=50,
        error_messages={
            'max_length': '请将描述信息限制在50个字符以内',
        },
    )
    users = forms.ModelMultipleChoiceField(
        required=False,
        queryset=User.objects.all(),
    )


class UserCreateForm(forms.Form):
    username = forms.CharField(
        required=True,
        max_length=20,
        error_messages={
            'required': '用户名不能为空',
            'max_length': '请将用户名限制在20个字符以内',
        },
    )
    email = forms.EmailField(
        required=True,
        error_messages={
            'invalid': '邮箱格式错误',
            'required': '邮箱不能为空',
        },
    )
    is_active = forms.ChoiceField(
        required=True,
        choices = UserStatusType.attrs.items(),
        error_messages={
            'invalid_choice': '非法的用户状态',
            'required': '用户状态不能为空',
        },
    )
    role = forms.ChoiceField(
        required=True,
        choices=UserRoleType.attrs.items(),
        error_messages={
            'invalid_choice': '非法的用户角色',
            'required': '用户角色不能为空',
        },
    )
    groups = forms.ModelMultipleChoiceField(
        required=False,
        queryset=UserGroup.objects.all(),
    )


class UserUpdateForm(forms.Form):
    is_active = forms.ChoiceField(
        required=True,
        choices = UserStatusType.attrs.items(),
        error_messages={
            'invalid_choice': '非法的用户状态',
            'required': '用户状态不能为空',
        },
    )
    role = forms.ChoiceField(
        required=True,
        choices=UserRoleType.attrs.items(),
        error_messages={
            'invalid_choice': '非法的用户角色',
            'required': '用户角色不能为空',
        },
    )
    groups = forms.ModelMultipleChoiceField(
        required=False,
        queryset=UserGroup.objects.all(),
    )
