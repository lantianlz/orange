# -*- coding: utf-8 -*-

import hashlib

from django.conf import settings
from django.utils.crypto import constant_time_compare  # , get_random_string
from django.utils.encoding import smart_str


class MD5PasswordHasher(object):

    def salt(self):
        return settings.SECRET_KEY

    def encode(self, password):
        # assert password
        return hashlib.md5(self.salt() + password).hexdigest()

    def make_password(self, password):
        # assert password
        return self.encode(smart_str(password))

    def check_password(self, password, encoded):
        return constant_time_compare(self.encode(smart_str(password)), encoded)
