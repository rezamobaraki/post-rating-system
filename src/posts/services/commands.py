from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction

from core.settings.third_parties.redis_templates import RedisKeyTemplates
from posts.models import Rate
from posts.models.post import Post
from posts.models.post_stat import PostStat

CACHE_TIMEOUT = settings.CACHE_TIMEOUT

User = get_user_model()


def update_or_create_rate(user, post, score):
    with transaction.atomic():
        rate, created = Rate.objects.update_or_create(
            user=user, post=post,
            defaults={'score': score}
        )
        # Trigger asynchronous stat update
        from posts.tasks import update_post_stats
        transaction.on_commit(lambda: update_post_stats.delay(post.id))

    return rate, created


@transaction.atomic
def get_or_create_stat(*, post: Post, rate: Rate) -> tuple[PostStat, bool]:
    stat, created = PostStat.objects.get_or_create(post=post)
    # TODO calculate by its weight: stat.average_rate += rate.score / (stat.rates_count+1)
    stat.average_rate = stat.average_rate * stat.rates_count + rate.score / (stat.rates_count + 1)
    stat.rates_count += 1
    stat.save()

    stats = {"average_rate": stat.average_rate, "rates_count": stat.rates_count}
    key = RedisKeyTemplates.format_post_stats_key(post_id=post.id)
    cache.set(key, stats, CACHE_TIMEOUT)

    return stat, created
