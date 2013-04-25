# -*- coding:utf8 -*-
__author__ = 'PyYoshi'

from Twiq.mode_manager import BaseMode

class MisakuraMode(BaseMode):
    """
    http://yellow.ribbon.to/~sc/misakura.js
    """
    mode_name = "みさくらモード"
    def __init__(self):
        super(MisakuraMode, self).__init__()