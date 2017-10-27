#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('LANG', 'en_US.UTF-8')

from meila_ops import settings


def main():
    try:
        python_interpreter = settings.PYTHON_INTERPRETER
        if not os.path.exists(python_interpreter):
            raise IOError
    except (AttributeError, IOError):
        python_interpreter = sys.executable
    finally:
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'navigator.py')
        cmd = ' '.join((python_interpreter, script))
        os.system(cmd)


if __name__ == '__main__':
    main()
