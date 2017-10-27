# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from collections import namedtuple, OrderedDict
from ConfigParser import ConfigParser
from tempfile import NamedTemporaryFile

from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase

from logic.db.meila_ops.models import AssetServer


class ResultCallback(CallbackBase):

    def __init__(self, *args, **kwargs):
        super(ResultCallback, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_failed = {}
        self.host_unreachable = {}

    def v2_runner_on_ok(self, result):
        self.host_ok[result._host.get_name()] = result._result

    def v2_runner_on_failed(self, result, ignore_errors):
        self.host_failed[result._host.get_name()] = result._result

    def v2_runner_on_unreachable(self, result):
        self.host_unreachable[result._host.get_name()] = result._result


class AnsibleRunner(object):

    def __init__(self, module_name, module_args, pattern='all', forks=10, gather_facts='no'):
        Options = namedtuple(
            'Options', [
                'connection', 'module_path', 'forks', 'become',
                'become_method', 'become_user', 'check',
            ]
        )
        self.module_name = module_name
        self.module_args = module_args
        self.pattern = pattern
        self.forks = forks
        self.gather_facts = gather_facts
        self.variable_manager = VariableManager()
        self.loader = DataLoader()
        self.options = Options(
            connection='smart', module_path='', forks=self.forks, become=None,
            become_method=None, become_user=None, check=False,
        )
        self.passwords = dict(vault_pass='')
        self.results_callback = ResultCallback()
        self.inventory_file = self._set_inventory_file()
        self.inventory = Inventory(
            loader=self.loader,
            variable_manager=self.variable_manager,
            host_list=self.inventory_file.name,
        )
        self.variable_manager.set_inventory(self.inventory)

    def run(self):
        play_source = dict(
            name = "Ansible PlayBook",
            hosts = self.pattern,
            gather_facts = self.gather_facts,
            tasks = [
                dict(action=dict(module=self.module_name, args=self.module_args)),
            ],
        )
        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)
        tqm = None
        try:
            tqm = TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                options=self.options,
                passwords=self.passwords,
                stdout_callback=self.results_callback,
            )
            result = tqm.run(play)
        finally:
            if tqm is not None:
                tqm.cleanup()
                self.inventory_file.close()
        return (
            self.results_callback.host_ok,
            self.results_callback.host_failed,
            self.results_callback.host_unreachable,
        )

    def _set_inventory_file(self):
        inventory_file = NamedTemporaryFile(delete=True)
        parser = ConfigParser()
        servers = AssetServer.objects.all()
        for server in servers:
            value_dict = OrderedDict([
                ('ansible_host', server.ip),
                ('ansible_port', server.port),
                ('ansible_user', server.adminaccount.username),
                ('ansible_ssh_pass', server.adminaccount.password),
            ])
            value = ' '.join(['{}={}'.format(k, v) for k, v in value_dict.iteritems()])
            parser.set(None, server.hostname, value)
        parser.write(inventory_file)
        inventory_file.flush()
        return inventory_file
