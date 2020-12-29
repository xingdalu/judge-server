import os
from typing import Union
import json

import redis

KEY_PREFIX = 'judge-server:submission'


def set(key: str, value: Union[str, dict], timeout: int, nx: bool = False):
    key = f'{KEY_PREFIX}:{key}'
    if isinstance(value, dict):
        value = json.dumps(value)
    return redis_client.set(key, value, timeout, nx=nx)


def get(key: str):
    key = f'{KEY_PREFIX}:{key}'
    value = redis_client.get(key)
    return value.decode() if value else value


def get_redis_pool(url):
    pool = redis.ConnectionPool.from_url(url)
    return redis.Redis(connection_pool=pool)


redis_client = get_redis_pool(os.environ.get('REDIS_URL'))
