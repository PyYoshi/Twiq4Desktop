# -*- coding:utf8 -*-
__author__ = 'PyYoshi'

import re

import tweepy
from tweepy import OAuthHandler, API, TweepError

RegexHttpUrl = re.compile(r'http://[A-Za-z0-9\'~+\-=_.,/%\?!;:@#\*&\(\)]+')
RegexHttpsUrl = re.compile(r'https://[A-Za-z0-9\'~+\-=_.,/%\?!;:@#\*&\(\)]+')

class Token(object):
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

class Twit(object):
    def __init__(self,consumer_token, access_token=None):
        if not isinstance(consumer_token, Token): raise Exception("consumer_token is invalid type!")
        self.auth = OAuthHandler(consumer_token.key, consumer_token.secret)
        self.api = None
        if access_token != None and isinstance(access_token, Token):
            # ok
            self.auth.set_access_token(access_token.key, access_token.secret)
            self.api = self._get_api(self.auth)

    def _get_api(self, auth):
        return API(auth,retry_count=3,cache=tweepy.MemoryCache(timeout=60))

    def get_auth_url(self):
        return self.auth.get_authorization_url()

    def get_access_token(self, pin):
        self.auth.get_access_token(pin)
        self.api = self._get_api(self.auth)
        return Token(self.auth.access_token.key, self.auth.access_token.secret)

    @classmethod
    def _get_msg_length(cls, msg):
        """
        https://dev.twitter.com/docs/api/1.1/get/help/configuration
        """
        msg = re.sub(RegexHttpUrl, "0123456789012345678901", msg)
        msg = re.sub(RegexHttpsUrl, "01234567890123456789012", msg)
        return len(msg)

    @classmethod
    def validate_msg(cls, msg):
        """
        Args:
            msg: str, 投稿するメッセージ
        Return:
            (is_valid:bool, reminder:int)
        """
        max_msg_length = 140
        is_valid = False
        msg_length = cls._get_msg_length(msg)
        reminder = 140 - msg_length
        if 0 < msg_length <= max_msg_length: is_valid = True
        return (is_valid, reminder)

    def post(self, msg):
        return self.api.update_status(status=msg)

    def undo_post(self):
        pass

    def verify_credentials(self, include_entities=True, skip_status=False):
        return self.api.verify_credentials(include_entities=include_entities, skip_status=skip_status)

    def get_user_timeline(self, screen_name, count=50):
        return self.api.user_timeline(screen_name=screen_name, count=count)

    def destroy_status(self, status_id):
        return self.api.destroy_status(id=status_id)
