from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.db.models import Avg, Case, Count, F, Sum, When
from django.db.models.functions import Coalesce, Round
from django.utils import timezone

from posts.models.post import Post
from posts.models.rate import Rate

CACHE_TIMEOUT = settings.CACHE_TIMEOUT


def update_post_cache(post: Post):
    average = Rate.objects.filter(post=post).aggregate(
        average=Coalesce(Round(Avg('score'), precision=1), 0.0)
    )['average']
    count = Rate.objects.filter(post=post).aggregate(count=Count('id'))['count']

    cache.set(post.cache_key_average, average, CACHE_TIMEOUT)
    cache.set(post.cache_key_count, count, CACHE_TIMEOUT)


def rates_average(*, post: Post) -> float:
    average = cache.get(post.cache_key_average)
    if average is None:
        average = Rate.objects.filter(post=post).aggregate(
            average=Coalesce(Round(Avg('score'), precision=1), 0.0)
        )['average']
        cache.set(post.cache_key_average, average, CACHE_TIMEOUT)
    return average


def rates_count(*, post: Post) -> int:
    count = cache.get(post.cache_key_count)
    if count is None:
        count = Rate.objects.filter(post=post).aggregate(count=Count('id'))['count']
        cache.set(post.cache_key_count, count, CACHE_TIMEOUT)
    return count


