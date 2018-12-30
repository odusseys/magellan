import json
import pickle as pkl
from typing import Generator
import re
import redis as r

from magellan.env import REDIS_HOST
from magellan.services.logging import get_logger

_DEFAULT_CACHE_DURATION = 300

logger = get_logger(__name__)


class _RedisMock:
    def __init__(self):
        self.store = {}
        pass

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value, ex=None):
        self.store[key] = value

    def rpush(self, key, value):
        items = self.store.get(key)
        if items is None:
            items = []
            self.store[key] = items
        items.append(value)

    def brpop(self, key, timeout):
        items = self.store.get(key)
        if not items:
            return None
        else:
            return items.pop()

    def delete(self, *keys):
        for key in keys:
            if key in self.store:
                del self.store[key]

    def lpush(self, *stuff):
        return

    def ltrip(self, *stuff):
        return

    def lrange(self, *stuff):
        return None

    def scan_iter(self, match):
        match = match.replace('*', '.*')
        return [k for k in self.store.keys() if re.search(match, k) is not None]

    def delete_all(self):
        self.store = {}


def _get_redis():
    if REDIS_HOST is None:
        logger.warn(
            "No REDIS_HOST in environment, using a local mock. Do not use in production !")
        return _RedisMock()
    port = 6379
    return r.StrictRedis(host=REDIS_HOST, port=port)


redis = _get_redis()


def test_connection():
    redis.get("test")


class Queue:
    def __init__(self, name):
        if name is None:
            raise ValueError("Must specify a queue name")
        self.name = name
        self._key = 'queue::{}'.format(self.name)

    def post_message_json(self, message: str):
        if redis is not None:
            redis.lpush(self._key, message)
        else:
            raise ValueError("No redis activated")

    def post_message_object(self, message: dict):
        self.post_message_json(json.dumps(message))

    def get_message(self, timeout=0):
        message = redis.brpop(self._key, timeout)
        if message is None:
            return None
        return json.loads(message[1].decode('utf-8'))

    def messages(self) -> Generator:
        while True:
            yield self.get_message()


def _cache_key(region: str, version: int, *args, **kwargs):
    arglist = [str(t) for t in args]
    kwarglist = ["{}={}".format(k, str(v)) for k, v in sorted(
        kwargs.items(), key=lambda x: x[0])]
    arglist.extend(kwarglist)
    key = ":".join(arglist)
    return "cache::{}::{}::{}".format(region, version, key)


def cached(region: str = None, version: int = 0, ttl=_DEFAULT_CACHE_DURATION):
    """

    :param region: the cache "region" in which to cache this function's results
    :param ttl:
    :return:
    """

    if region is not None and "::" in region:
        raise ValueError("Region name cannot contain ::")

    def decorator(f):
        cache_region = region
        if cache_region is None:
            cache_region = "{}.{}".format(f.__module__, f.__name__)

        def wrapper(*args, **kwargs):
            key = _cache_key(cache_region, version, *args, **kwargs)
            value = redis.get(key)
            if value is not None:
                try:
                    return pkl.loads(value)
                except:
                    # the object is probably coming from an earlier version of the api.
                    # we just drop the cache. not even necessary, but cleaner.
                    redis.delete(key)
            # the object is not in the cache. We pickle it and add it to the cache
            value = f(*args, **kwargs)
            redis.set(key, pkl.dumps(value), ex=ttl)
            return value

        # add invalidation utilities through monkeypatching
        def invalidate_all():
            for key in redis.scan_iter(match="cache::{}::*".format(cache_region)):
                redis.delete(key)

        def invalidate(*args, **kwargs):
            redis.delete(_cache_key(cache_region, version, *args, **kwargs))

        wrapper.invalidate_all = invalidate_all
        wrapper.invalidate = invalidate

        return wrapper

    return decorator


class BufferQueue:
    def __init__(self, limit, *args):
        suffix = ":".join(map(str, args))
        self.key = "{}:{}".format("buffer", suffix)
        self.limit = limit

    def push(self, item):
        redis.lpush(self.key, item)
        redis.ltrim(self.key, 0, self.limit - 1)

    def get(self):
        return redis.lrange(self.key, 0, self.limit - 1)

    def clear(self):
        redis.ltrim(self.key, 1, 0)

    def __repr__(self):
        return 'BufferQueue({})'.format(self.get())
