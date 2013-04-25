# -*- coding:utf8 -*-
__author__ = 'PyYoshi'

from Twiq.mode_manager import BaseMode

class NormalMode(BaseMode):
    mode_name = "通常モード"

    def __init__(self):
        super(NormalMode, self).__init__()

    def post(self, tw, notification_func, msg, in_reply_to_status_id=None):
        return tw.post(msg)