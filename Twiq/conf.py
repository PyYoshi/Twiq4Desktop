# -*- coding:utf8 -*-
__author__ = 'PyYoshi'

import cPickle as pickle
import os
import glob
import re

from Twiq import _, APP_CONFIG_DIR_PATH

RegexAccountConfig = re.compile(r'^account\.([A-Za-z0-9]+)\.config')

class AppConfig:
    def __init__(self, consumer_key='BPAHaczcVkyiCMGD3sgJA', consumer_secret_key='pf55I7c8afemY1V8fycwpWNtSJLmlzdvfLCOdQyDYsM'):
        self.consumer_key = consumer_key
        self.consumer_secret_key = consumer_secret_key
        self.selected_account = None
        self.selected_mode = None

class AccountConfig:
    def __init__(self, screen_name, user_id, access_key, access_secret_key):
        self.screen_name = screen_name
        self.user_id = user_id
        self.access_key = access_key
        self.access_secret_key = access_secret_key

# TODO: pickleファイルをuuidを使って暗号化(http://docs.python.jp/2/library/uuid.html?highlight=uuid#uuid)

def _read_config(config_path, enc=False):
    """
    コンフィグファイルが読み込めないならデフォルトのものを使えばいいだけなので
    例外を起こす必要がない。returnがNoneであればそのままAppConfigを使えばいい

    Return:
        None or AppConfig
    """
    config = None
    if os.path.exists(config_path):
        try:
            config_fp = open(config_path, 'rb')
            try:
                config = pickle.load(config_fp)
            finally:
                config_fp.close()
        except pickle.PickleError as e:
            _.error(msg=u'コンフィグファイルはpickleでdumpされたファイルではないようです。: %s' % e.message, extra={'position': 'conf.read_config'})
        except IOError as e:
            _.error(msg=u'コンフィグファイルを読み込めませんでした。: %s' % e.message, extra={'position': 'conf.read_config'})
        except Exception as e:
            _.error(msg=u'なんらかの要因でコンフィグファイルを読み込めませんでした。: %s' % e.message, extra={'position': 'conf.read_config'})
    return config

def _save_config(config_path, config, enc=False):
    """

    """
    fp = open(config_path,'wb')
    try:
        pickle.dump(config, fp)
    finally:
        fp.close()

def findAll_account_config():
    curdir = os.path.curdir
    os.chdir(APP_CONFIG_DIR_PATH)
    files = glob.glob('account.*.config')
    os.chdir(curdir)
    return files

def get_accounts_list():
    accounts = []
    for f in findAll_account_config():
        m = re.search(RegexAccountConfig, f)
        if m:
            accounts.append(m.group(1))
    return accounts

def read_app_config():
    config_path = os.path.join(APP_CONFIG_DIR_PATH, 'app.config')
    return _read_config(config_path)

def save_app_config(config):
    # TODO: IO処理はthreadingしたい
    config_path = os.path.join(APP_CONFIG_DIR_PATH, 'app.config')
    _save_config(config_path, config)

def read_account_config(account_name):
    config_path = os.path.join(APP_CONFIG_DIR_PATH, 'account.%s.config' % account_name)
    return _read_config(config_path)

def save_account_config(account_name,config):
    # TODO: IO処理はthreadingしたい
    config_path = os.path.join(APP_CONFIG_DIR_PATH, 'account.%s.config' % account_name)
    _save_config(config_path, config)

def delete_account_config(account_name):
    config_path = os.path.join(APP_CONFIG_DIR_PATH, 'account.%s.config' % account_name)
    os.remove(config_path)
