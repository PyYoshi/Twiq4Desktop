# -*- coding:utf8 -*-
__author__ = 'PyYoshi'

import os
from os.path import expanduser
import logging

__all__ = ['_', 'APP_NAME','HOME_PATH','APP_CONFIG_DIR_PATH','TW','MODE']

APP_NAME = 'twiq'
HOME_PATH = expanduser('~')
APP_CONFIG_DIR_PATH = os.path.join(HOME_PATH, '.' + APP_NAME)
APP_PLUGINS_DIR_PATH = os.path.join(APP_CONFIG_DIR_PATH, 'plugins')
LOG_FILE = os.path.join(APP_CONFIG_DIR_PATH, 'app.log')

# APPホームディレクトリの作成
if not os.path.exists(APP_CONFIG_DIR_PATH): os.mkdir(APP_CONFIG_DIR_PATH)

# ロガー
def get_logger(level):
    logging.basicConfig(level=level, format='%(asctime)s, %(position)s, %(levelname)s: %(message)s', filename=LOG_FILE)
    return logging.getLogger(APP_NAME)
_ = get_logger(logging.DEBUG)
