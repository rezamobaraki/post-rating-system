import time

from django.conf import settings
from django.core.cache import cache
from rest_framework.exceptions import Throttled

from commons.messages.error_messages import ErrorMessages
from core.settings.third_parties.redis_templates import RedisKeyTemplates


class FraudDetection:
    rate_limit_period = settings.RATE_LIMIT_PERIOD
    max_rates_per_hour = settings.MAX_RATES_PER_HOUR
    suspicious_threshold = settings.SUSPICIOUS_THRESHOLD
    time_threshold = settings.TIME_THRESHOLD
    last_actions_to_track = settings.LAST_ACTIONS_TO_TRACK

    @classmethod
    def check_rate_limit(cls, user_id: int) -> None:
        """
        Checks if the user has exceeded the rate limit for a specific post.
        """
        rate_limit_key = RedisKeyTemplates.format_rate_limit_key(user_id)
        current_count = cache.get(rate_limit_key, 0)
        if current_count >= cls.max_rates_per_hour:
            raise Throttled(
                detail=ErrorMessages.RATE_LIMIT_EXCEEDED.message, code=ErrorMessages.RATE_LIMIT_EXCEEDED.code
            )
        cache.set(rate_limit_key, current_count + 1, cls.rate_limit_period)

    @classmethod
    def detect_suspicious_activity(cls, post_id: int) -> bool:
        """
        Checks for suspicious activity based on the number of rating actions within a certain time frame.
        """
        fraud_detect_key = RedisKeyTemplates.format_fraud_detect_key(post_id)
        recent_actions = cache.lrange(fraud_detect_key, 0, -1)

        if len(recent_actions) >= cls.suspicious_threshold:
            first_action_time = float(recent_actions[0])
            current_time = time.time()
            if current_time - first_action_time < cls.time_threshold:
                return True

        cache.lpush(fraud_detect_key, time.time())
        cache.ltrim(fraud_detect_key, 0, cls.last_actions_to_track - 1)
        cache.expire(fraud_detect_key, cls.time_threshold)
        return False

    @classmethod
    def is_fraudulent_action(cls, user_id: int, post_id: int) -> bool:
        cls.check_rate_limit(user_id)
        return cls.detect_suspicious_activity(post_id)
