# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models

from logic.utils.encryptor import AESCipher


class AESCipherField(models.CharField):

    def __init__(self, *args, **kwargs):
        super(AESCipherField, self).__init__(*args, **kwargs)
        self.cipher = AESCipher(settings.SECRET_KEY[:16])

    def get_prep_value(self, value):
        ciphertext = self.cipher.encrypt(value)
        return ciphertext

    def get_db_prep_value(self, value, connection, prepared=False):
        value = '' if value is None else value
        return self.get_prep_value(value)

    def from_db_value(self, value, expression, connection, context):
        plaintext = self.cipher.decrypt(value)
        return plaintext

models.AESCipherField = AESCipherField
