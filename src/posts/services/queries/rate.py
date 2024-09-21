from django.db.models import Avg, Q
from django.db.models.functions import Coalesce, Round

from posts.models import Rate


def get_updated_rates(post, last_update):
    """Filter rates that created or updated after last_update of post_stats"""
    return Rate.objects.filter(post_id=post.id).filter(
        Q(created_at__gt=last_update) | Q(updated_at__gt=last_update)
    )


def calculate_average_rates(post, suspected_rates_threshold):
    total_rates = Rate.objects.filter(post_id=post.id).count()
    suspected_rates_count = Rate.objects.filter(post_id=post.id, is_suspected=True).count()

    if total_rates == 0:
        return 0.0

    if suspected_rates_count < total_rates * suspected_rates_threshold:
        """consider as normal rates"""
        return Rate.objects.filter(post_id=post.id).aggregate(
            average=Coalesce(Round(Avg('score'), precision=1), 0.0)
        )['average']
    else:
        """Remove suspected rates from the average calculation"""
        return Rate.objects.filter(post_id=post.id, is_suspected=False).aggregate(
            average=Coalesce(Round(Avg('score'), precision=1), 0.0)
        )['average']
