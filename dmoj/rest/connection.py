import redis

from dmoj.judgeenv import env


def get_redis_pool():
    pool = redis.ConnectionPool(host=env.redis.host, port=env.redis.port, db=0)
    return redis.Redis(connection_pool=pool)
