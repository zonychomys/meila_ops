# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import namedtuple

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from logic.comm_def import (
    UserRoleType, AssetType, AssetStatusType,
)


class UserGroup(models.Model):
    name = models.CharField(verbose_name='名称', max_length=20, unique=True)
    desc = models.CharField(verbose_name='备注', max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = '用户组'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class User(AbstractUser):
    email = models.EmailField(verbose_name='邮箱', unique=True)
    role = models.PositiveSmallIntegerField(verbose_name='用户类型', choices=UserRoleType.attrs.items())
    groups = models.ManyToManyField(verbose_name='用户组', to=UserGroup)
    avatar = models.ImageField(verbose_name='头像', upload_to='avatar', blank=True, null=True)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username

    def get_privileged_assets(self):
        permissions_id = self.groups.values_list('permission__id', flat=True)
        related_permissions = Permission.objects.filter(id__in=permissions_id)
        related_permissions = related_permissions.union(self.permission_set.all())
        privileged_assets = AssetServer.objects.none()
        for permission in related_permissions:
            assets_id = permission.asset_groups.values_list('asset__assetserver__id', flat=True)
            privileged_assets = privileged_assets | AssetServer.objects.filter(id__in=assets_id)
            privileged_assets = privileged_assets | permission.assets.all()
        return privileged_assets.distinct()

    def get_inventory_info(self):
        inventories = []
        for asset in self.get_privileged_assets():
            for account in asset.account_set.all():
                Inventory = namedtuple('Inventory', ['user', 'asset', 'account'])
                inventory = Inventory(user=self, asset=asset, account=account)
                inventories.append(inventory)
        return inventories


class AssetGroup(models.Model):
    name = models.CharField(verbose_name='名称', max_length=20, unique=True)
    type = models.PositiveSmallIntegerField(verbose_name='资产类型', choices=AssetType.attrs.items())
    desc = models.CharField(verbose_name='备注', max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = '资产组'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Asset(models.Model):
    type = models.PositiveSmallIntegerField(verbose_name='资产类型', choices=AssetType.attrs.items())
    groups = models.ManyToManyField(verbose_name='资产组', to=AssetGroup)
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=AssetStatusType.attrs.items())

    class Meta:
        verbose_name = '资产'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s' % self.id

    def get_asset_label(self):
        for field in self._meta.get_fields():
            if field.one_to_one is True and hasattr(self, field.get_accessor_name()):
                return eval('self.%s' % field.get_accessor_name()).__str__()


class AssetServer(models.Model):
    hostname = models.CharField(verbose_name='主机名', max_length=20, unique=True)
    ip = models.GenericIPAddressField(verbose_name='IP')
    port = models.PositiveIntegerField(verbose_name='端口', blank=True, null=True)
    cpu = models.CharField(verbose_name='CPU', max_length=20, blank=True, null=True)
    ram = models.CharField(verbose_name='内存', max_length=20, blank=True, null=True)
    disk = models.CharField(verbose_name='硬盘', max_length=50, blank=True, null=True)
    os = models.CharField(verbose_name='操作系统', max_length=20, blank=True, null=True)
    asset = models.OneToOneField(verbose_name='资产', to=Asset, on_delete=models.CASCADE)

    class Meta:
        verbose_name = '服务器'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.hostname


class AdminAccount(models.Model):
    username = models.CharField(verbose_name='账户', max_length=20)
    password = models.AESCipherField(verbose_name='密码', max_length=64, blank=True, null=True)
    server = models.OneToOneField(verbose_name='服务器', to=AssetServer, on_delete=models.CASCADE)

    class Meta:
        verbose_name = '管理账户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class Account(models.Model):
    servers = models.ManyToManyField(verbose_name='服务器', to=AssetServer)
    username = models.CharField(verbose_name='账户', max_length=20)
    password = models.AESCipherField(verbose_name='密码', max_length=64, blank=True, null=True)
    desc = models.CharField(verbose_name='备注', max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = '系统账户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class Permission(models.Model):
    name = models.CharField(verbose_name='名称', max_length=20, unique=True)
    users = models.ManyToManyField(verbose_name='用户', to=User)
    user_groups = models.ManyToManyField(verbose_name='用户组', to=UserGroup)
    assets = models.ManyToManyField(verbose_name='资产', to=AssetServer)
    asset_groups = models.ManyToManyField(verbose_name='资产组', to=AssetGroup)
    desc = models.CharField(verbose_name='备注', max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = '权限规则'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Audit(models.Model):
    user = models.ForeignKey(verbose_name='用户', to=User)
    asset = models.ForeignKey(verbose_name='资产', to=AssetServer)
    account = models.ForeignKey(verbose_name='账户', to=Account)
    pid = models.PositiveSmallIntegerField(verbose_name='进程ID')
    remote_ip = models.GenericIPAddressField(verbose_name='远程IP')
    start_time = models.DateTimeField(verbose_name='开始时间', auto_now_add=True)
    end_time = models.DateTimeField(verbose_name='结束时间', blank=True, null=True)
    is_active = models.BooleanField(verbose_name='是否在线')

    class Meta:
        verbose_name = '审计信息'
        verbose_name_plural = verbose_name
        ordering = ('-start_time',)

    def __str__(self):
        return '%s' % self.id


class AuditExecute(models.Model):
    audit = models.ForeignKey(verbose_name='审计信息', to=Audit)
    time = models.DateTimeField(verbose_name='执行时间', auto_now=True)
    command = models.TextField(verbose_name='命令')

    class Meta:
        verbose_name = '命令执行记录'
        verbose_name_plural = verbose_name
        ordering = ('time',)

    def __str__(self):
        return '%s' % self.id
