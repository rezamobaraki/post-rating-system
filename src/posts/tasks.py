import logging

from celery import shared_task
from django.conf import settings
from django.core.cache import cache

from commons.messages.log_messges import LogMessages
from core.settings.third_parties.redis_templates import RedisKeyTemplates
from posts.models import Post, PostStat, Rate
from posts.services.commands.post_stat import update_cache_post_stats, update_post_stat
from posts.services.queries.rate import calculate_average_rates, get_updated_rates

logger = logging.getLogger(__name__)


@shared_task
def apply_pending_rates():
    """
    Apply pending rates to the Rate asynchronously.
    """
    key = RedisKeyTemplates.pending_rates_key()
    if pending_rates := cache.get(key, []):
        from posts.services.commands.rate import bulk_update_or_create_rates
        bulk_update_or_create_rates(rate_data=pending_rates)
        cache.delete(key)


@shared_task
def bulk_update_or_create_post_stats(*, scores: dict):
    post_id_list = scores.keys()
    post_stats = PostStat.objects.filter(post_id__in=post_id_list)

    """update existing post stats"""
    for post_stat in post_stats:
        new_score = scores[post_stat.post_id]["score"]
        total_score = post_stat.average_rates * post_stat.total_rates
        post_stat.average_rates = (total_score + new_score) / post_stat.total_rates
    if post_stats:
        PostStat.objects.bulk_update(post_stats, ['average_rates', 'total_rates'])

    """create new post stats"""
    missing_post_ids = set(post_id_list).difference(post_stats.values_list('post_id', flat=True))
    new_post_stats = [
        PostStat(
            post_id=post_id,
            average_rates=scores[post_id]["score"] / scores[post_id]["count"],
            total_rates=scores[post_id]["count"]
        ) for post_id in missing_post_ids
    ]
    created_obj = PostStat.objects.bulk_create(new_post_stats)

    """update cache"""
    update_cache_post_stats(post_stats=[*post_stats, *created_obj])


@shared_task
def update_post_stats_periodical():
    """
        Update the average rates and total rates of the post periodically.
        note: it will consider number of rates that created or updated after updated_at or created_at in post_stat
    """
    try:
        for post in Post.objects.all():
            post_stat, created = PostStat.objects.get_or_create(post_id=post.id)
            last_update = post_stat.updated_at if not created else post.created_at

            updated_rates = get_updated_rates(post, last_update)

            if updated_rates.exists():
                average_rates = calculate_average_rates(post, settings.SUSPECTED_RATES_THRESHOLD)
                total_rates = Rate.objects.filter(post_id=post.id).count()
                update_post_stat(post, average_rates, total_rates)
            else:
                logger.info(LogMessages.no_new_rate(post_id=post.id))

    except Exception as e:
        logger.error(LogMessages.error_update_post_stats(error=e))
