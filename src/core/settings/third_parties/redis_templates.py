import dataclasses


@dataclasses.dataclass(frozen=True)
class RedisKeyTemplates:
    POST_STATS: str = "post:{post_id}:stats"
    RATE_LIMIT: str = "rate_limit:{user_id}:{post_id}"
    SUSPICIOUS_ACTIVITY: str = "suspicious_activity:{post_id}"

    @classmethod
    def format_post_stats_key(cls, post_id: int) -> str:
        return cls.POST_STATS.format(post_id=post_id)

    @classmethod
    def format_rate_limit_key(cls, user_id: int, post_id: int) -> str:
        return cls.RATE_LIMIT.format(user_id=user_id, post_id=post_id)

    @classmethod
    def format_suspicious_activity_key(cls, post_id: int) -> str:
        return cls.SUSPICIOUS_ACTIVITY.format(post_id=post_id)
