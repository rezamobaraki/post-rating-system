import dataclasses


@dataclasses.dataclass(frozen=True)
class RedisKeyTemplates:
    POST_STATS: str = "post:{post_id}:stats"
    POST_STATS_LOCK: str = "post:{post_id}:stat_lock"
    RATE_LIMIT: str = "rate_limit:{user_id}"
    FRAUD_DETECT: str = "fraud_detect:{post_id}"

    @classmethod
    def format_post_stats_key(cls, post_id: int) -> str:
        return cls.POST_STATS.format(post_id=post_id)

    @classmethod
    def format_post_stats_lock_key(cls, post_id: int) -> str:
        return cls.POST_STATS_LOCK.format(post_id=post_id)

    @classmethod
    def format_rate_limit_key(cls, user_id: int) -> str:
        return cls.RATE_LIMIT.format(user_id=user_id)

    @classmethod
    def format_fraud_detect_key(cls, post_id: int) -> str:
        return cls.FRAUD_DETECT.format(post_id=post_id)
