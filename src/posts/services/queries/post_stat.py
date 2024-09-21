from django.conf import settings
from django.core.cache import cache

from core.settings.third_parties.redis_templates import RedisKeyTemplates
from posts.models.post_stat import PostStat


def get_post_stat(*, post_id: int):
    key = RedisKeyTemplates.format_post_stats_key(post_id=post_id)
    stats = cache.get(key)

    if not stats:
        post_stat = PostStat.objects.filter(post_id=post_id).first()
        if post_stat:
            stats = {
                'average_rates': post_stat.average_rates,
                'total_rates': post_stat.total_rates
            }
            cache.set(key, stats, timeout=settings.CACHE_TIMEOUT)
        else:
            stats = {'average_rates': 0, 'total_rates': 0}

    return stats
