import logging

from django.conf import settings
from django.core.cache import cache
from django.db import transaction

from commons.messages.log_messges import LogMessages
from core.settings.third_parties.redis_templates import RedisKeyTemplates
from posts.models import PostStat

logger = logging.getLogger(__name__)

def update_cache_post_stats(*, post_stats: list[PostStat]):
    """
    we can use mSet of redis to set multiple keys at once
    """
    for post_stat in post_stats:
        stats = {"average_rates": post_stat.average_rates, "total_rates": post_stat.total_rates}
        key = RedisKeyTemplates.format_post_stats_key(post_id=post_stat.id)
        cache.set(key, stats, settings.CACHE_TIMEOUT)


def update_post_stat(post, average_rates, total_rates):
    with transaction.atomic():
        PostStat.objects.filter(post_id=post.id).update(
            average_rates=average_rates,
            total_rates=total_rates
        )
    cache.delete(RedisKeyTemplates.format_post_stats_key(post_id=post.id))
    logger.info(
        LogMessages.update_post_stats(post_id=post.id, average_rates=average_rates, total_rates=total_rates)
    )
