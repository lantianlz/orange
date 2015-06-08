# -*- coding: utf-8 -*-

from django.contrib.sessions.backends.base import SessionBase, CreateError
from common import cache

KEY_PREFIX = "session_orange_"


class SessionStore(SessionBase):

    """
    A cache-based session store.
    """

    def __init__(self, session_key=None):
        self._cache = cache.Cache(cache.CACHE_SESSION)
        super(SessionStore, self).__init__(session_key)

    @property
    def cache_key(self):
        return KEY_PREFIX + self._get_or_create_session_key()

    def load(self):
        try:
            session_data = self._cache.get(self.cache_key, None)
        except Exception:
            # Some backends (e.g. memcache) raise an exception on invalid
            # cache keys. If this happens, reset the session. See #17810.
            session_data = None
        if session_data is not None:
            return session_data
        self.create()
        return {}

    def create(self):
        # Because a cache can fail silently (e.g. memcache), we don't know if
        # we are failing to create a new session because of a key collision or
        # because the cache is missing. So we try for a (large) number of times
        # and then raise an exception. That's the risk you shoulder if using
        # cache backing.
        for i in xrange(3):
            self._session_key = self._get_new_session_key()
            try:
                self.save(must_create=True)
            except CreateError:
                continue
            self.modified = True
            return
        raise RuntimeError("Unable to create a new session key.")

    def save(self, must_create=False):
        self._cache.set(self.cache_key, self._get_session(no_load=must_create), self.get_expiry_age())

        # if must_create:
        #     func = self._cache.add
        # else:
        #     func = self._cache.set
        # result = func(self.cache_key,
        #               self._get_session(no_load=must_create),
        #               self.get_expiry_age())

        # if must_create and not result:
        #     raise CreateError

    def exists(self, session_key):
        return self._cache.exists(KEY_PREFIX + session_key)

    def delete(self, session_key=None):
        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key
        self._cache.delete(KEY_PREFIX + session_key)
