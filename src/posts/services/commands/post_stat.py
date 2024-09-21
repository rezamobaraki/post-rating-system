from django.conf import settings
from django.core.cache import cache

from core.settings.third_parties.redis_templates import RedisKeyTemplates
from posts.models import PostStat


def update_cache_post_stats(*, post_stats: list[PostStat]):
    for post_stat in post_stats:
        stats = {"average_rates": post_stat.average_rates, "total_rates": post_stat.total_rates}
        key = RedisKeyTemplates.format_post_stats_key(post_id=post_stat.id)
        cache.set(key, stats, settings.CACHE_TIMEOUT)
