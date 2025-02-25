import random
import time
from typing import Self
import redis as r

class RateLimitExceed(Exception):
    pass


class RateLimiter:
    def __init__(self: Self, redis: r.Redis) -> None:
        self._redis = redis


    def test(self) -> bool:
        now = time.time()
        self._redis.zremrangebyscore("api_rate_limit", "-inf", now - 3)
        self._redis.zadd("api_rate_limit", {str(now): now})
        return self._redis.zcard("api_rate_limit") < 5  # type: ignore


def make_api_request(rate_limiter: RateLimiter):
    if not rate_limiter.test():
        raise RateLimitExceed
    else:
        # какая-то бизнес логика
        pass


if __name__ == '__main__':
    redis = r.Redis()
    rate_limiter = RateLimiter(redis)

    for _ in range(50):
        time.sleep(random.randint(1, 2))

        try:
            make_api_request(rate_limiter)
        except RateLimitExceed:
            print("Rate limit exceed!")
        else:
            print("All good")

