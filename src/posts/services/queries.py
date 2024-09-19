from django.conf import settings
from django.core.cache import cache

from core.settings.third_parties.redis_templates import RedisKeyTemplates
from posts.models import Post
from posts.models.post_stat import PostStat

CACHE_TIMEOUT = settings.CACHE_TIMEOUT


def get_post_stats(*, post: Post):
    key = RedisKeyTemplates.format_post_stats_key(post_id=post.id)
    stats = cache.get(key)

    if not stats:
        try:
            post_stat = PostStat.objects.get(post_id=post.id)
            stats = {
                'average_rate': post_stat.average_rate,
                'total_rates': post_stat.total_rates
            }
            cache.set(key, stats, timeout=CACHE_TIMEOUT)
        except PostStat.DoesNotExist:
            stats = {'average_rate': 0, 'total_rates': 0}

    return stats

