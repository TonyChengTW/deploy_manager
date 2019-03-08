# Copyright 2019 104 Job Bank Inc. All rights reserved
# Version: 0.1
# tony.cheng@104.com.tw

import redis
import json


class Cache(object):

    def __init__(self):
        self.redis_conn = None

    def create_redis_connection(self, host='127.0.0.1', port='6379'):
        try:
            pool = redis.ConnectionPool(host=host, port=port, decode_responses=True)
            self.redis_conn = redis.Redis(connection_pool=pool)
            return self.redis_conn
        except RuntimeError:
            raise

    def get_cache(self, namespace, key):
        try:
            redis_resp = self.redis_conn.hget(namespace, key)
            if redis_resp is None:
                return None
            else:
                return json.loads(redis_resp)
        except RuntimeError:
            raise

    def set_cache(self, namespace, value):
        try:
            self.redis_conn.hmset(namespace, value)
            return 1
        except RuntimeError:
            raise

    def check_cache(self, namespace):
        try:
            if len(self.redis_conn.hgetall(namespace)) != 0:
                return True         # is exist
            else:
                return False        # is not exist
        except RuntimeError:
            raise

    def del_cache(self, namespace):
        try:
            self.redis_conn.delete(namespace)
            return 1
        except RuntimeError:
            raise
