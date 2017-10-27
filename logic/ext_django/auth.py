# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.backends import ModelBackend

from logic.comm_def import UserRoleType
from logic.db.meila_ops.models import User


class EmailAuthModelBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

    def user_can_authenticate(self, user):
        is_active = getattr(user, 'is_active', None)
        is_superuser = True if user.role == UserRoleType.admin else False
        if is_active and is_superuser:
            return True
        else:
            return False
