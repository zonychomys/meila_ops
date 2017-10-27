# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from logic.utils.storage import Const


class UserStatusType(Const):
    inactive = (0, '禁用')
    active = (1, '激活')


class UserRoleType(Const):
    admin = (0, '管理员')
    user = (1, '普通用户')


class AssetType(Const):
    server = (0, '服务器')


class AssetStatusType(Const):
    unused = (0, '禁用')
    inused = (1, '启用')
