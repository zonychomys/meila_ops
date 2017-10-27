#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import fcntl
import getpass
import operator
import os
import pyte
import re
import select
import signal
import socket
import struct
import sys
import termios
import textwrap
import tty

import django
import paramiko
from django.utils.timezone import utc
from prompt_toolkit import prompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.validation import Validator, ValidationError
from pygments.token import Token
from termcolor import colored

reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meila_ops.settings')
django.setup()

from logic.db.meila_ops.models import (
    User, AssetServer, Permission, Audit, AuditExecute,
)


class Navigator(object):

    def __init__(self):
        self._user = User.objects.get(username=getpass.getuser())
        self._inventory = self._user.get_inventory_info()
        self._history = InMemoryHistory()
        self._completer = WordCompleter(
            words=['help', 'show', 'attach', 'exit'],
            ignore_case=True,
            sentence=True,
            match_middle=True,
        )

    def authentication(self):
        if not self._user.is_active:
            msg = '账户未激活或处于禁用状态, 请联系管理员'
            sys.stdout.write(colored(textwrap.dedent(msg), 'red', attrs=[]))
            sys.exit(0)
        else:
            self._show_nav_info()

    def interactive_loop(self):
        while True:
            try:
                line_buffer = prompt(
                    get_prompt_tokens=self._get_prompt_tokens,
                    style=self._get_prompt_style(),
                    history=self._history,
                    auto_suggest=AutoSuggestFromHistory(),
                    completer=self._completer,
                    complete_while_typing=True,
                    validator=ReplValidator(),
                ).strip().lower().split()
                if not line_buffer:
                    continue
                else:
                    option = line_buffer[0]
                    parameters = line_buffer[1:]
            except (EOFError, KeyboardInterrupt):
                sys.stdout.write('\n')
                sys.exit(0)
            else:
                if option == 'help':
                    self._show_help_info()
                elif option == 'show':
                    self._show_inventory()
                elif option == 'attach':
                    serial = int(parameters[0])
                    self._invoke_shell(serial)
                elif option == 'exit':
                    sys.stdout.write('\n')
                    sys.exit(0)
                else:
                    pass

    def _show_nav_info(self):
        nav_info = '''
        * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
        *                                                             *
        *                     欢迎登录美啦跳板机                      *
        *                                                             *
        * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

        '''
        sys.stdout.write(colored(textwrap.dedent(nav_info), 'cyan', attrs=[]))

    def _show_help_info(self):
        pass

    def _show_inventory(self):
        title = '{serial} {hostname} {ip} {account}\n'.format(
            serial='ID'.ljust(10),
            hostname='Hostname'.ljust(15),
            ip='IP'.ljust(25),
            account='Account'.ljust(10),
        )
        body = [
            '{serial} {hostname} {ip} {account}'.format(
                serial=str(c).ljust(10),
                hostname=value.asset.hostname.ljust(15),
                ip=value.asset.ip.ljust(25),
                account=value.account.username.ljust(10),
            ) for c, value in enumerate(self._inventory)
        ]
        sys.stdout.write(colored(title, 'grey', 'on_cyan', attrs=[]))
        sys.stdout.write('\n'.join(body) + '\n\n')

    def _invoke_shell(self, serial):
        user, asset, account = self._inventory[serial]
        channel = Channel(user, asset, account)
        channel.connect()

    def _get_prompt_style(self):
        style = style_from_dict({
            Token.User: '#ffff00',
            Token.Prompt: '#009900',
            Token.Path: '#1989fa',
            Token.Menu.Completions.Completion.Current: '#000000 bg:#009999',
            Token.Menu.Completions.Completion: '#000000 bg:#ffffff',
        })
        return style

    def _get_prompt_tokens(self, cli):
        tokens = [
            (Token.User, '(' + self._user.username + ')'),
            (Token.Prompt, '➜'),
            (Token.Path, ' /  '),
        ]
        return tokens

    @property
    def inventory(self):
        return self._inventory


class Channel(object):

    def __init__(self, user, asset, account):
        self.user = user
        self.asset = asset
        self.account = account
        self.pid = os.getpid()
        self.remote_ip = os.environ.get('SSH_CLIENT').split()[0]
        self.stream = pyte.ByteStream()
        self.screen = pyte.Screen(80, 24)
        self.stream.attach(self.screen)
        self.typing = False
        self.vim_is_active = False
        self.vim_try_close = False
        self.raw_cmdline = ''
        self.cleaned_cmdline = ''
        self.ps1_pattern = r'\[?.*@.*\]?[\$#]\s'
        self.vim_launch_pattern = r'vi[m]?\s*.*'
        self.vim_close_pattern = r'\x1b\[\d*;1H:\x1b\[\?25h\x1b\[\?0c[qx]'
        signal.signal(signal.SIGWINCH, self._set_terminal_size)

    def connect(self):
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(
                hostname=self.asset.ip,
                port=self.asset.port,
                username=self.account.username,
                password=self.account.password,
                timeout=10,
            )
        except socket.error:
            sys.stdout.write('Connection timed out.\n')
        except paramiko.ssh_exception.AuthenticationException:
            sys.stdout.write('Authentication failed.\n')
        else:
            transport = ssh.get_transport()
            transport.set_keepalive(interval=30)
            transport.use_compression(compress=True)
            size = self._get_terminal_size()
            self.channel = transport.open_session()
            self.channel.get_pty(term='linux', width=size[0], height=size[1])
            self.channel.invoke_shell()
            self._interactive_shell(self.channel)
            self.channel.close()
        finally:
            ssh.close()

    def _interactive_shell(self, chan):
        audit = Audit.objects.create(
            user=self.user,
            asset=self.asset,
            account=self.account,
            pid=self.pid,
            remote_ip=self.remote_ip,
            is_active=True,
        )
        audit.refresh_from_db()
        oldtty = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            tty.setcbreak(sys.stdin.fileno())
            chan.settimeout(0.0)
            while True:
                try:
                    r, w, e = select.select([chan, sys.stdin], [], [])
                    flag = fcntl.fcntl(sys.stdin, fcntl.F_GETFL, 0)
                    fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, flag|os.O_NONBLOCK)
                except Exception:
                    pass
                if chan in r:
                    try:
                        x = paramiko.py3compat.u(chan.recv(1024))
                        if len(x) == 0:
                            break
                        if self.typing:
                            self.raw_cmdline += x
                        if self.vim_try_close:
                            if re.findall(self.ps1_pattern, x):
                                self.vim_is_active = False
                                self.vim_try_close = False
                        sys.stdout.write(x)
                        sys.stdout.flush()
                    except socket.timeout:
                       pass
                if sys.stdin in r:
                    self.typing = True
                    x = os.read(sys.stdin.fileno(), 1024)
                    if len(x) == 0:
                        break
                    chan.send(x)
                    if x == '\r':
                        self.cleaned_cmdline = self._clean_raw_cmdline(self.raw_cmdline)
                        if not self.vim_is_active:
                            AuditExecute.objects.create(
                                audit=audit,
                                command=self.cleaned_cmdline,
                            )
                        if re.findall(self.vim_launch_pattern, self.cleaned_cmdline):
                            self.vim_is_active = True
                        if re.findall(self.vim_close_pattern, self.raw_cmdline):
                            self.vim_try_close = True
                        self.typing = False
                        self.raw_cmdline = ''
                        self.cleaned_cmdline = ''
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)
            audit.is_active = False
            audit.end_time = datetime.datetime.utcnow().replace(tzinfo=utc)
            audit.save()

    def _clean_raw_cmdline(self, raw_cmdline):
        self.stream.feed(raw_cmdline)
        cleaned_cmdline = ''
        for line in reversed(self.screen.buffer.values()):
            cleaned_cmdline = ''.join(map(operator.attrgetter('data'), line.values()))
            if cleaned_cmdline:
                break
        cleaned_cmdline = re.sub(self.ps1_pattern, '', cleaned_cmdline).strip()
        self.screen.reset()
        return cleaned_cmdline

    def _get_terminal_size(self):
        if 'TIOCGWINSZ' in dir(termios):
            TIOCGWINSZ = termios.TIOCGWINSZ
        else:
            TIOCGWINSZ = 1074295912
        s = struct.pack(str('HHHH'), 0, 0, 0, 0)
        x = fcntl.ioctl(sys.stdout.fileno(), TIOCGWINSZ, s)
        return struct.unpack('HHHH', x)[0:2][::-1]

    def _set_terminal_size(self, signalnum, handler):
        try:
            size = self._get_terminal_size()
            self.channel.resize_pty(*size)
        except Exception, e:
            pass


class ReplValidator(Validator, Navigator):

    def __init__(self):
        Validator.__init__(self)
        Navigator.__init__(self)

    def validate(self, document):
        self.text = document.text
        line_buffer = document.text.strip().lower().split()
        if not line_buffer:
            pass
        else:
            option = line_buffer[0]
            parameters = line_buffer[1:]
            if option in self._completer.words:
                try:
                    impl = getattr(self, '_validate_%s' % option)
                except AttributeError:
                    pass
                else:
                    return impl(parameters)
            else:
                raise ValidationError(
                    message='不存在的命令: %s' % option,
                    cursor_position=len(document.text),
                )

    def _validate_help(self, parameters):
        pass

    def _validate_show(self, parameters):
        pass

    def _validate_attach(self, parameters):
        if (not parameters or
            not parameters[0].isdigit() or
            len(parameters) > 1):
            raise ValidationError(
                message='选项attach需要传入一个整数类型的资产ID',
                cursor_position=len(self.text),
            )
        else:
            try:
                serial = int(parameters[0])
                self.inventory[serial]
            except IndexError:
                raise ValidationError(
                    message='不存在的资产ID',
                    cursor_position=len(self.text),
                )
            else:
                return True

    def _validate_exit(self, parameters):
        pass


def main():
    navigator = Navigator()
    navigator.authentication()
    navigator.interactive_loop()


if __name__ == '__main__':
    main()
