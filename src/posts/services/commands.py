from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from django.db.models import F

from core.settings.third_parties.redis_templates import RedisKeyTemplates
from posts.models import Rate
from posts.models.post_stat import PostStat
from posts.tasks import update_post_stats_async, update_stats_on_threshold_async

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


# TODO: Decide whether to keep this function or not
@transaction.atomic
def update_or_create_stat(*, post_id: int, new_score: int) -> tuple[PostStat, bool]:
    stat, created = PostStat.objects.update_or_create(
        post_id=post_id,
        defaults={
            'average_rates': (F('average_rates') * F('total_rates') + new_score) / (F('total_rates') + 1),
            'total_rates': F('total_rates') + 1
        }
    )
    stats = {"average_rates": stat.average_rate, "total_rates": stat.rates_count}
    key = RedisKeyTemplates.format_post_stats_key(post_id=post_id)
    cache.set(key, stats, settings.CACHE_TIMEOUT)

    return stat, created
