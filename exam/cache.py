import os

import redis


class RedisManagerClient:

    def __init__(self):
        self.client = redis.Redis(
            host=os.getenv("REDIS_HOST"),
            password=os.getenv("REDIS_PASSWORD"),
            port=os.getenv("REDIS_PORT"),
            socket_timeout=1  # 1sec
        )
