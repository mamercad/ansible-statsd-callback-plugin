# (C) 2020, Mark Mercado <mmercado@digitalocean.com>

# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

# import requests
from pprint import pprint
# from requests.auth import HTTPBasicAuth
import logging
import os
import socket

from ansible.plugins.callback import CallbackBase
from ansible import constants as C
from __main__ import cli

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

DOCUMENTATION = '''
    callback: statsd_callback_plugin
    type: notification
    short_description: Send callback on various runners to a statsd endpoint.
    description:
      - On ansible runner calls report state and task output to a statsd endpoint.
    requirements:
      - python socket library
    '''


class StatsD():

    STATSD_HOST = os.getenv('STATSD_HOST', default='127.0.0.1')
    STATSD_PORT = os.getenv('STATSD_PORT', default=9125)

    def __init__(self, *args, **kwargs):
        self.project = kwargs.get('project')
        self.playbook = kwargs.get('playbook')

    def ship_it(self, metric):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(metric.encode(), (self.STATSD_HOST, self.STATSD_PORT))
            logging.debug(f"Sent metric {metric} to StatD")
        except Exception as e:
            logging.critical(f"Failed to sent metric {metric} to StatD: {e}")

    def emit_playbook_start(self, playbook):
        metric = "ansible.playbook_start.{}.{}.{}.{}.{}:1|c".format(
            self.project,
            self.playbook,
            playbook['_basedir'].replace(".", "_").replace("/", "_"),
            playbook['_file_name'].replace(".", "_"),
            "/".join(map(str, playbook['_entries'])),
        )
        self.ship_it(metric)

    def emit_runner_ok(self, result):
        metric = "ansible.runner_ok.{}.{}.{}.{}.{}:1|c".format(
            self.project,
            self.playbook,
            result['_host'],
            str(result['_task']).replace("TASK: ", ""),
            result['_result']['changed'],
        )
        self.ship_it(metric)

    def emit_runner_failed(self, result):
        metric = "ansible.runner_failed.{}.{}.{}.{}.{}:1|c".format(
            self.project,
            self.playbook,
            result['_host'],
            str(result['_task']).replace("TASK: ", ""),
            result['_result']['changed'],
        )
        self.ship_it(metric)

    def emit_playbook_stats(self, stats):
        for k1 in stats.keys():
            if len(stats[k1]):
                for k2 in stats[k1].keys():
                    metric = "ansible.playbook_stats.{}.{}.{}.{}:1|c".format(
                        self.project,
                        self.playbook,
                        k1,
                        k2,
                    )
                    self.ship_it(metric)


class CallbackModule(CallbackBase):

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'statsd_callback_plugin'

    def __init__(self, *args, **kwargs):
        super(CallbackModule, self).__init__()
        logging.basicConfig(level=logging.DEBUG)
        self.statsd = StatsD(project="foo", playbook="bar")

    def v2_playbook_on_start(self, playbook):
        self._display.display(
            "*** v2_playbook_on_start ***", color=C.COLOR_DEBUG)
        self.statsd.emit_playbook_start(playbook.__dict__)

    # def v2_playbook_on_play_start(self, play):
    #     self.play = play
    #     print("*** v2_playbook_on_play_start ***")
    #     # pprint(play.__dict__)
    #     self.extra_vars = self.play.get_variable_manager().extra_vars
    #     print('==== extra_vars ====')
    #     pprint(self.extra_vars)
    #     # self.callback_url = self.extra_vars['callback_url']
    #     # self.username = self.extra_vars['username']
    #     # self.password = self.extra_vars['password']
    #     # print('\nExtra vars that were passed to playbook are accessible to the callback plugin by calling the variable_manager on the play object for the method v2_playbook_on_play_start:\nextra_vars: {0}'.format(self.extra_vars))

    def v2_runner_on_ok(self, result):
        self._display.display("*** v2_runner_on_ok ***", color=C.COLOR_DEBUG)
        self.statsd.emit_runner_ok(result.__dict__)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self._display.display(
            "*** v2_runner_on_failed ***", color=C.COLOR_DEBUG)
        self.statsd.emit_runner_failed(result.__dict__)

    def v2_playbook_on_stats(self, stats):
        self._display.display(
            "*** v2_playbook_on_stats ***", color=C.COLOR_DEBUG)
        self.statsd.emit_playbook_stats(stats.__dict__)
