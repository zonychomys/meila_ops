# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
import os

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from passlib.hash import sha512_crypt

from logic.ansible.runner import AnsibleRunner
from logic.comm_def import UserStatusType, UserRoleType
from logic.db.meila_ops.models import User
from logic.ext_django.decorators import nonlogin_required
from .forms import LoginForm, SetPasswordForm, InitializeForm


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class IndexView(View):

    def get(self, request):
        return render(request, 'core/index.html')


@method_decorator(nonlogin_required, name='dispatch')
class LoginView(View):

    def get(self, request):
        if self.is_require_initialize():
            return HttpResponseRedirect(reverse('core:Initialize'))
        else:
            captcha_key = CaptchaStore.generate_key()
            captcha_url = captcha_image_url(captcha_key)
            context = dict(
                captcha_key=captcha_key,
                captcha_url=captcha_url,
            )
            return render(request, 'core/login.html', context)

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect(reverse('core:Index'))
            else:
                try:
                    user = User.objects.get(email=username)
                except User.DoesNotExist:
                    error_msg = '该邮箱账号不存在'
                else:
                    if not user.is_active:
                        error_msg = '该邮箱账号未激活或处于禁用状态'
                    elif not user.role == UserRoleType.admin:
                        error_msg = '登录管理后台需要管理员账号权限'
                    else:
                        error_msg = '邮箱账号或密码错误'
                finally:
                    captcha_key = CaptchaStore.generate_key()
                    captcha_url = captcha_image_url(captcha_key)
                    context = dict(
                        error_msg=error_msg,
                        captcha_key=captcha_key,
                        captcha_url=captcha_url,
                    )
                    return render(request, 'core/login.html', context)
        else:
            captcha_key = CaptchaStore.generate_key()
            captcha_url = captcha_image_url(captcha_key)
            context = dict(
                form=form,
                captcha_key=captcha_key,
                captcha_url=captcha_url,
            )
            return render(request, 'core/login.html', context)

    def is_require_initialize(self):
        return True if not User.objects.count() else False


@method_decorator(login_required(redirect_field_name=None), name='dispatch')
class LogoutView(View):

    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('core:Index'))


@method_decorator(nonlogin_required, name='dispatch')
class SetPasswordView(View):

    def get(self, request):
        sign = request.GET.get('sign')
        email = request.GET.get('email')
        if sign == hashlib.md5(email + settings.SECRET_KEY).hexdigest():
            context = dict(
                email=email,
            )
            return render(request, 'core/set_password.html', context)
        else:
            return HttpResponseForbidden()

    def post(self, request):
        form = SetPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            user.refresh_from_db()
            runner = AnsibleRunner(
                module_name='user',
                module_args=dict(
                    state='present',
                    name=user.username,
                    password=sha512_crypt.using(rounds=5000).hash(password),
                    shell=os.path.join(settings.BASE_DIR, 'utils/startup.py'),
                    generate_ssh_key='yes',
                ),
                pattern='localhost',
            )
            host_ok, host_failed, host_unreachable = runner.run()
            return HttpResponseRedirect(reverse('core:Login'))
        else:
            email = request.POST.get('email')
            context = dict(
                form=form,
                email=email,
            )
            return render(request, 'core/set_password.html', context)


@method_decorator(nonlogin_required, name='dispatch')
class InitializeView(View):

    def get(self, request):
        return render(request, 'core/initialize.html')

    def post(self, request):
        form = InitializeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = User.objects.create_user(
                email=email,
                username='admin',
                is_active=UserStatusType.active,
                role=UserRoleType.admin,
            )
            user.set_password(password)
            user.save()
            user.refresh_from_db()
            runner = AnsibleRunner(
                module_name='user',
                module_args=dict(
                    state='present',
                    name=user.username,
                    password=sha512_crypt.using(rounds=5000).hash(password),
                    shell=os.path.join(settings.BASE_DIR, 'utils/startup.py'),
                    generate_ssh_key='yes',
                ),
                pattern='localhost',
            )
            host_ok, host_failed, host_unreachable = runner.run()
            return HttpResponseRedirect(reverse('core:Login'))
        else:
            context = dict(
                form=form,
            )
            return render(request, 'core/initialize.html', context)
