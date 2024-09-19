from datetime import timedelta

from celery import shared_task
from django.core.cache import cache
from django.db.models import Avg, Count
from django.db.models.functions import Coalesce, Round
from django.utils import timezone

from core.settings.third_parties.redis_templates import RedisKeyTemplates
from posts.models import Post, PostStat, Rate


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
