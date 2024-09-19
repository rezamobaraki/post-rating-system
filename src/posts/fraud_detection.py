import time

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.exceptions import Throttled

from core.env import env
from core.settings.third_parties.redis_templates import RedisKeyTemplates
from posts.models import Post

User = get_user_model()


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


def is_fraudulent_activity(user: User, post: Post) -> bool:
    fraud_key = f"fraud_check:user:{user.id}:post:{post.id}"
    recent_actions = cache.lrange(fraud_key, 0, -1)

    # If more than 5 rating actions within 60 seconds, flag as fraud
    if len(recent_actions) >= 5:
        first_action_time = float(recent_actions[0])
        current_time = time.time()
        if current_time - first_action_time < 60:
            return True

    # Record the current action
    cache.lpush(fraud_key, time.time())
    cache.ltrim(fraud_key, 0, 4)  # Keep the last 5 actions
    cache.expire(fraud_key, 60)  # Set a TTL of 60 seconds

    return False
