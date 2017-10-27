# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os


os.environ.setdefault('ANSIBLE_HOST_KEY_CHECKING', 'False')
os.environ.setdefault('ANSIBLE_SSH_ARGS', '-C -o ControlMaster=no -o ControlPersist=60s')
