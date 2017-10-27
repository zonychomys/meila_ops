# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64

from Crypto import Random
from Crypto.Cipher import AES


class AESCipher(object):

    def __init__(self, key):
        self.key = key
        self.block_size = 16

    def pad(self, text):
        pad_char = chr(self.block_size - len(text) % self.block_size)
        pad_num = self.block_size - (len(text) % self.block_size)
        return text + pad_char * pad_num

    def unpad(self, text):
        pad_char = text[-1:]
        pad_num = ord(pad_char)
        return text[:-pad_num]

    def encrypt(self, plaintext):
        plaintext = self.pad(plaintext)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(plaintext))

    def decrypt(self, ciphertext):
        ciphertext = base64.b64decode(ciphertext)
        iv = ciphertext[:self.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self.unpad(cipher.decrypt(ciphertext[self.block_size:]))
