# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict


class ConstMetaclass(type):

    def __new__(cls, name, bases, attrs):
        new_attrs = {}
        new_attrs_attrs = {}
        new_attrs_values = {}
        new_attrs_labels = {}

        for k, v in attrs.items():
            if k.startswith('__'):
                continue
            if isinstance(v, tuple):
                new_attrs[k] = v[0]
                new_attrs_attrs[v[0]] = v[1]
                new_attrs_values[k] = v[0]
                new_attrs_labels[k] = v[1]
            else:
                new_attrs_values[k] = v
                new_attrs_labels[k] = v

        new_attrs_attrs = sorted(new_attrs_attrs.iteritems(), key=lambda (k, v): k)
        new_attrs_attrs = OrderedDict(new_attrs_attrs)
        new_attrs['attrs'] = new_attrs_attrs
        new_attrs['values'] = new_attrs_values
        new_attrs['labels'] = new_attrs_labels
        return type.__new__(cls, name, bases, new_attrs)


class Const(object):
    __metaclass__ = ConstMetaclass
