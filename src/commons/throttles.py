import time

from django.core.cache import cache
from rest_framework.throttling import BaseThrottle, UserRateThrottle

from core.env import env


class LoginRateThrottle(UserRateThrottle):
    scope = 'login'


class RegisterRateThrottle(UserRateThrottle):
    scope = 'register'


class PostRateThrottle(BaseThrottle):
    rate = env.int("POST_RATE_LIMIT", 1000)
    cache_timeout = env.int("CACHE_TIMEOUT", 3600)
    cache_key = 'post_rate_limit'

    def get_cache_key(self):
        """
        Returns the cache key for the global request counter.
        """
        return self.cache_key

    def allow_request(self, request, view):
        """
        Determines whether the request should be allowed.
        """
        cache_key = self.get_cache_key()
        request_count = cache.get(cache_key, 0)

        if request_count >= self.rate:
            # Too many requests, block further access
            return False

        # Otherwise, increment the request count
        cache.incr(cache_key, 1) if cache.get(cache_key) else cache.set(cache_key, 1, self.cache_timeout)
        return True

    def wait(self):
        """
        Returns the number of seconds until the throttle is reset.
        """
        return self.cache_timeout - (time.time() % self.cache_timeout)
