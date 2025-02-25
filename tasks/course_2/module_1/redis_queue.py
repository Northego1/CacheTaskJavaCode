import datetime
import json
from typing import Self

import redis as r


class RedisQueue:
    def __init__(self: Self, redis: r.Redis, queue_name: str = "MyQueue") -> None:
        self._redis = redis
        self.queue_name = queue_name


    def publish(
            self: Self,
            msg: dict,
    ):
        self._redis.rpush(self.queue_name, json.dumps(msg))


    def consume(self: Self) -> dict | None:
        value = self._redis.lpop(self.queue_name)
        if value:
            return json.loads(value) # type: ignore
        return None

if __name__ == '__main__':
    redis = r.Redis()
    q = RedisQueue(redis)

    q.publish({'a': 1})
    q.publish({'b': 2})
    q.publish({'c': 3})

    assert q.consume() == {'a': 1}
    assert q.consume() == {'b': 2}
    assert q.consume() == {'c': 3}
    assert q.consume() == None



