# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from captcha.fields import CaptchaField


class LoginForm(forms.Form):
    username = forms.EmailField(
        required=True,
        error_messages={
            'invalid': '邮箱格式错误',
            'required': '用户名不能为空',
        },
    )
    password = forms.CharField(
        required=True,
        error_messages={
            'required': '密码不能为空',
        },
    )
    captcha = CaptchaField(
        required=True,
        error_messages = {
            'invalid': '验证码错误',
            'required': '验证码不能为空',
        },
    )


class SetPasswordForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(
        required=True,
        min_length=8,
        max_length=30,
        error_messages={
            'required': '密码不能为空',
            'min_length': '密码长度应大于8个字符',
            'max_length': '密码长度应限制在30个字符以内',
        },
    )


class InitializeForm(forms.Form):
    email = forms.EmailField(
        required=True,
        error_messages={
            'invalid': '邮箱格式错误',
            'required': '邮箱不能为空',
        },
    )
    password = forms.CharField(
        required=True,
        min_length=8,
        max_length=30,
        error_messages={
            'required': '密码不能为空',
            'min_length': '密码长度应大于8个字符',
            'max_length': '密码长度应限制在30个字符以内',
        },
    )
