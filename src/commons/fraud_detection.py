import time

import redis
from django.conf import settings

from core.settings.third_parties.redis_templates import RedisKeyTemplates

redis_client = redis.StrictRedis.from_url(settings.REDIS_LOCATION)


class FraudDetection:
    rate_limit_period = settings.RATE_LIMIT_PERIOD
    suspicious_threshold = settings.SUSPICIOUS_THRESHOLD
    time_threshold = settings.TIME_THRESHOLD
    last_actions_to_track = settings.LAST_ACTIONS_TO_TRACK

    @classmethod
    def detect_suspicious_activity(cls, post_id: int) -> bool:
        """
        Checks for suspicious activity based on the number of rating actions within a certain time frame.
        """
        fraud_detect_key = RedisKeyTemplates.format_fraud_detect_key(post_id)
        recent_actions = redis_client.lrange(fraud_detect_key, 0, -1)

        if len(recent_actions) >= cls.suspicious_threshold:
            first_action_time = float(recent_actions[0])
            current_time = time.time()
            if current_time - first_action_time < cls.time_threshold:
                return True

        redis_client.lpush(fraud_detect_key, time.time())
        redis_client.ltrim(fraud_detect_key, 0, cls.last_actions_to_track - 1)
        redis_client.expire(fraud_detect_key, cls.time_threshold)
        return False

    @classmethod
    def is_fraudulent_action(cls, post_id: int) -> bool:
        return cls.detect_suspicious_activity(post_id)
