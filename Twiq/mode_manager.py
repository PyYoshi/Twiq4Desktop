# -*- coding:utf8 -*-
__author__ = 'PyYoshi'

from yapsy.IPlugin import IPlugin
from yapsy.PluginManager import PluginManager

__all__ = ['BaseMode']

class BaseMode(IPlugin):
    mode_name = None
    def __init__(self):
        super(BaseMode, self).__init__()

    def post(self, tw, notification_func, status, in_reply_to_status_id=None):
        raise NotImplementedError()

