from django.conf import settings
from django.core.cache import cache

from posts.models.post import Post
from posts.models.stat import PostRateStat

CACHE_TIMEOUT = settings.CACHE_TIMEOUT


def get_stat(*, post: Post) -> PostRateStat:
    stat = cache.get(post.cache_key_stat)

def rates_average(*, post: Post) -> float:
    average = cache.get(post.cache_key_average)
    if average is None:
        average = PostRateStat.objects.filter(post=post).only('avg_rate').first().avg_rate
        cache.set(post.cache_key_average, average, CACHE_TIMEOUT)
    return average


def rates_count(*, post: Post) -> int:
    count = cache.get(post.cache_key_count)
    if count is None:
        count = PostRateStat.objects.filter(post=post).only('cnt_rate').first().cnt_rate
        cache.set(post.cache_key_count, count, CACHE_TIMEOUT)
    return count

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
