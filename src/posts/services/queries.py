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

# def calculate_weighted_average(post: Post):
#     now = timezone.now()
#     time_threshold = now - timedelta(hours=24)
#
#     recent_weight = 0.3
#     established_weight = 0.7
#
#     rates = Rate.objects.filter(post=post).annotate(
#         weight=Case(
#             When(created_at__gte=time_threshold, then=recent_weight),
#             default=established_weight,
#         )
#     )
#
#     weighted_sum = rates.aggregate(
#         weighted_sum=Coalesce(Sum(F('score') * F('weight')), 0.0)
#     )['weighted_sum']
#
#     total_weight = rates.aggregate(
#         total_weight=Coalesce(Sum('weight'), 0.0)
#     )['total_weight']
#
#     if total_weight > 0:
#         return Round(weighted_sum / total_weight, precision=1)
#     return 0.0
