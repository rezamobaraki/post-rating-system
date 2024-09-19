from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.cache import cache
from django.db.models import Avg, Count
from django.db.models.functions import Coalesce, Round
from django.utils import timezone

from core.settings.third_parties.redis_templates import RedisKeyTemplates
from posts.models import Post, PostStat, Rate


@shared_task
def update_post_stats_async(post_id, rate_id):
    post = Post.objects.get(id=post_id)
    rate = Rate.objects.get(id=rate_id)

    # Lock to prevent race conditions
    lock_key = f"post:{post.id}:stat_lock"
    with cache.lock(lock_key, timeout=10):
        stat, created = PostStat.objects.get_or_create(post=post)
        stat.average_rate = (stat.average_rate * stat.total_rates + rate.score) / (stat.total_rates + 1)
        stat.total_rates += 1
        stat.save()

        cache.set(RedisKeyTemplates.format_post_stats_key(post.id), {
            "average_rate": stat.average_rate,
            "total_rates": stat.total_rates
        }, settings.CACHE_TIMEOUT)


@shared_task
def update_post_stats(*, post: Post):
    # Get rates within the last hour to detect sudden spikes
    recent_time = timezone.now() - timedelta(hours=1)
    recent_rates = Rate.objects.filter(post_id=post.id, created_at__gte=recent_time)

    # Check for suspicious activity
    if recent_rates.count() > 1000:  # Arbitrary threshold, adjust as needed
        # Implement more sophisticated fraud detection here
        # For now, we'll just skip the update
        return

    # Calculate new stats

    all_rates = Rate.objects.filter(post_id=post.id).aggregate(
        average=Coalesce(Round(Avg('score'), precision=1), 0.0),
        total=Count('id')
    )

    # Update or create PostStat
    PostStat.objects.update_or_create(
        post_id=post_id,
        defaults={
            'average_rate': all_rates['average'],
            'total_rates': all_rates['total']
        }
    )

    # Clear cache to ensure fresh data on next read
    cache.delete(RedisKeyTemplates.format_post_stats_key(post_id=post.id))
