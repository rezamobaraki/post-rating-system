from django.conf import settings
from django.core.cache import cache
from django.db import transaction

from posts.models import Rate
from posts.models.post import Post
from posts.models.stat import Stat

CACHE_TIMEOUT = settings.CACHE_TIMEOUT


@transaction.atomic
def get_or_create_stat(*, post: Post, rate: Rate) -> tuple[Stat, bool]:
    stat, created = Stat.objects.get_or_create(post=post)
    stat.average_rate = stat.average_rate * stat.rates_count + rate.score / (stat.rates_count + 1)
    stat.rates_count += 1
    stat.save()

    cache.set(post.cache_key_average, stat.average_rate, CACHE_TIMEOUT)
    cache.set(post.cache_key_count, stat.rates_count, CACHE_TIMEOUT)

    return stat, created
