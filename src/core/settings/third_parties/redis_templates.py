import dataclasses


@dataclasses.dataclass(frozen=True)
class RedisKeyTemplates:
    PENDING_RATES: str = "pending_rates"
    POST_STATS: str = "post:{post_id}:stats"
    POST_STATS_LOCK: str = "post:{post_id}:stat_lock"
    FRAUD_DETECT: str = "fraud_detect:{post_id}"

    @classmethod
    def format_post_stats_key(cls, post_id: int) -> str:
        return cls.POST_STATS.format(post_id=post_id)

    @classmethod
    def format_post_stats_lock_key(cls, post_id: int) -> str:
        return cls.POST_STATS_LOCK.format(post_id=post_id)

    @classmethod
    def format_fraud_detect_key(cls, post_id: int) -> str:
        return cls.FRAUD_DETECT.format(post_id=post_id)

    @classmethod
    def pending_rates_key(cls) -> str:
        return cls.PENDING_RATES
