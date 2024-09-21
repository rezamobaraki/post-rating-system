import logging

from celery import shared_task
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db.models import Avg, Q
from django.db.models.functions import Coalesce, Round

from commons.messages.log_messges import LogMessages
from core.settings.third_parties.redis_templates import RedisKeyTemplates
from posts.models import Post, PostStat, Rate
from posts.services.commands.post_stat import update_cache_post_stats

logger = logging.getLogger(__name__)


@shared_task
def apply_pending_rates():
    """
    Apply pending rates to the Rate asynchronously.
    """
    key = RedisKeyTemplates.pending_rates_key()
    pending_rates = cache.get(key, [])
    if pending_rates:
        bulk_update_or_create_post_stats(scores=pending_rates)
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
        number of rates that created or updated after updated_at or created_at in post_stat
    """
    try:
        posts = Post.objects.all()
        for post in posts:
            post_stat, created = PostStat.objects.get_or_create(post_id=post.id)
            last_update = post_stat.updated_at if not created else post.created_at

            """Filter rates created or updated after the last update"""
            rates = Rate.objects.filter(post_id=post.id).filter(
                Q(created_at__gt=last_update) | Q(updated_at__gt=last_update)
            )

            if rates.exists():
                total_rates = Rate.objects.filter(post_id=post.id).count()
                suspected_rates_count = Rate.objects.filter(post_id=post.id, is_suspected=True).count()

                if total_rates == 0:
                    average_rates = 0.0
                else:
                    if suspected_rates_count < total_rates * settings.SUSPECTED_RATES_THRESHOLD:
                        average_rates = Rate.objects.filter(post_id=post.id).aggregate(
                            average=Coalesce(Round(Avg('score'), precision=1), 0.0)
                        )['average']
                    else:
                        """Remove suspected rates from the average calculation"""
                        average_rates = Rate.objects.filter(post_id=post.id, is_suspected=False).aggregate(
                            average=Coalesce(Round(Avg('score'), precision=1), 0.0)
                        )['average']

                with transaction.atomic():
                    PostStat.objects.filter(post_id=post.id).update(
                        average_rates=average_rates,
                        total_rates=total_rates
                    )
                cache.delete(RedisKeyTemplates.format_post_stats_key(post_id=post.id))
                logger.info(
                    LogMessages.update_post_stats(post_id=post.id, average_rates=average_rates, total_rates=total_rates)
                )
            else:
                logger.info(LogMessages.no_new_rate(post_id=post.id))

    except Exception as e:
        logger.error(LogMessages.error_update_post_stats(error=e))
