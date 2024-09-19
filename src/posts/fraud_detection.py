from django.conf import settings
from django.core.cache import cache
from rest_framework.exceptions import Throttled

from core.env import env
from core.settings.third_parties.redis_templates import RedisKeyTemplates


class FraudDetectionSystem:
    def __init__(self):
        self.keys = RedisKeyTemplates
        self.rate_limit_period = env.int("RATE_LIMIT_PERIOD", default=3600)
        self.max_rates_per_hour = env.int("MAX_RATES_PER_HOUR", default=10)
        self.suspicious_threshold = env.int("SUSPICIOUS_THRESHOLD", default=1000)

    def check_rate_limit(self, user_id, post_id):
        key = self.keys.format_rate_limit_key(user_id, post_id)
        count = cache.get(key, 0)
        if count >= self.max_rates_per_hour:
            raise Throttled(detail="Rate limit exceeded. Please try again later.")
        cache.set(key, count + 1, self.rate_limit_period)

    def check_suspicious_activity(self, post_id):
        key = self.keys.format_suspicious_activity_key(post_id)
        count = cache.get(key, 0)
        cache.set(key, count + 1, settings.CACHE_TIMEOUT)
        return count >= self.suspicious_threshold

    def is_fraudulent(self, user_id, post_id):
        self.check_rate_limit(user_id, post_id)
        return self.check_suspicious_activity(post_id)


fraud_detection = FraudDetectionSystem()
