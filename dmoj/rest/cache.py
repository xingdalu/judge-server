import os
from typing import Union
import json

import redis

KEY_PREFIX = 'submission'


def set(key: str, value: Union[str, dict], timeout: int):
    key = f'{KEY_PREFIX}:{key}'
    if isinstance(value, dict):
        value = json.dumps(value)
    return redis_client.set(key, value, timeout)


def get(key: str):
    key = f'{KEY_PREFIX}:{key}'
    value = redis_client.get(key)
    return value.decode() if value else value


def get_redis_pool(host, port, db=0):
    pool = redis.ConnectionPool(host=host, port=port, db=db)
    return redis.Redis(connection_pool=pool)


redis_client = get_redis_pool(os.environ.get('REDIS_HOST'), os.environ.get('REDIS_PORT'))
