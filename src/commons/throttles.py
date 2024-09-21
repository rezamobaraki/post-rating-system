import time

from django.conf import settings
from django.core.cache import cache
from rest_framework.throttling import BaseThrottle, UserRateThrottle

from core.env import env


class LoginRateThrottle(UserRateThrottle):
    scope = 'login'


class RegisterRateThrottle(UserRateThrottle):
    scope = 'register'


class UserHourlyPostRateThrottle(UserRateThrottle):
    scope = 'user_hourly'
    rate = f'{settings.MAX_RATES_PER_HOUR}/hour'

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            return f"{self.scope}:{request.user.pk}"
        return None


class PostRateThrottle(BaseThrottle):
    rate = env.int("POST_RATE_LIMIT", 1000)
    cache_timeout = env.int("CACHE_TIMEOUT", 3600)
    cache_key = 'post_rate_limit'

    def get_cache_key(self):
        return self.cache_key

    def allow_request(self, request, view):
        cache_key = self.get_cache_key()
        request_count = cache.get(cache_key, 0)

        if request_count >= self.rate:
            """Too many requests, block further access"""
            return False

        """ Otherwise, increment the request count"""
        cache.incr(cache_key, 1) if cache.get(cache_key) else cache.set(cache_key, 1, self.cache_timeout)
        return True

    def wait(self):
        """
        Returns the number of seconds until the throttle is reset.
        """
        return self.cache_timeout - (time.time() % self.cache_timeout)
