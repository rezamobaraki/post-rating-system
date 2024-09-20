from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from django.db.models import F

from core.settings.third_parties.redis_templates import RedisKeyTemplates
from posts.models import Rate
from posts.models.post_stat import PostStat
from posts.tasks import update_post_stats_async, update_stats_on_threshold_async

CACHE_TIMEOUT = settings.CACHE_TIMEOUT

User = get_user_model()


def update_or_create_rate(*, user_id: int, post_id: int, score: int, is_suspected=False):
    with transaction.atomic():
        rate, created = Rate.objects.update_or_create(
            user_id=user_id, post_id=post_id,
            defaults={'score': score, 'is_suspected': is_suspected}
        )
        if is_suspected:
            transaction.on_commit(lambda: update_stats_on_threshold_async.delay(post_id))
            return rate, created
        transaction.on_commit(lambda: update_post_stats_async.delay(post_id))
    return rate, created


@transaction.atomic
def get_or_create_stat(*, post_id: int, new_score: int) -> tuple[PostStat, bool]:
    stat, created = PostStat.objects.update_or_create(
        post_id=post_id,
        defaults={
            'average_rate': (F('average_rate') * F('rates_count') + new_score) / (F('rates_count') + 1),
            'rates_count': F('rates_count') + 1
        }
    )
    stats = {"average_rate": stat.average_rate, "rates_count": stat.rates_count}
    key = RedisKeyTemplates.format_post_stats_key(post_id=post_id)
    cache.set(key, stats, CACHE_TIMEOUT)

    return stat, created
