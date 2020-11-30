from typing import Union
import json

from dmoj.rest.app import app

KEY_PREFIX = 'submission'


def set(key: str, value: Union[str, dict], timeout: int):
    key = f'{KEY_PREFIX}:{key}'
    if isinstance(value, dict):
        value = json.dumps(value)
    return app.state.redis.set(key, value, timeout)


def get(key: str):
    key = f'{KEY_PREFIX}:{key}'
    value = app.state.redis.get(key)
    return value.decode() if value else value
