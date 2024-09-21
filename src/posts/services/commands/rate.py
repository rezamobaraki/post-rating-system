from django.core.cache import cache

from core.settings.third_parties.redis_templates import RedisKeyTemplates
from posts.models import Rate
from posts.tasks import bulk_update_or_create_post_stats

# TODO : it should be in settings env.int(BULK_THRESHOLD,50)
BULK_THRESHOLD = 50
CACHE_TIMEOUT = 15 * 60  # 15 minutes


def update_or_create_rate(*, user_id: int, post_id: int, score: int, is_suspected=False):
    key = RedisKeyTemplates.pending_rates_key()
    pending_rates = cache.get(key, [])
    pending_rates.append({'user_id': user_id, 'post_id': post_id, 'score': score, 'is_suspected': is_suspected})
    """
    There are some situation that system will shutdown so we should enable redis to store in file system
    Update: persist=True -> AOF (Append Only File) or RDB (Redis Database Backup)
    """
    cache.set(key, pending_rates, timeout=CACHE_TIMEOUT)

    if len(pending_rates) >= BULK_THRESHOLD:
        bulk_update_or_create_rates(pending_rates)
        cache.delete(key)


def bulk_update_or_create_rates(rate_data: list[dict]):
    existing_rates = Rate.objects.filter(
        user_id__in=[rate['user_id'] for rate in rate_data],
        post_id__in=[rate['post_id'] for rate in rate_data]
    )

    rate_lookup = {(rate.user_id, rate.post_id): rate for rate in existing_rates}
    new_scores = {rate["post_id"]: {"score": 0, "count": 0} for rate in rate_data}
    new_rates, updated_rates = [], []

    for rate in rate_data:
        user_id, post_id, score, is_suspected = rate['user_id'], rate['post_id'], rate['score'], rate['is_suspected']
        if (user_id, post_id) in rate_lookup:
            existing_rate = rate_lookup[(user_id, post_id)]
            new_scores[post_id]["score"] += score - existing_rate.score
            existing_rate.score, existing_rate.is_suspected = score, is_suspected
            updated_rates.append(existing_rate)
        else:
            new_scores[post_id]["score"] += score
            new_scores[post_id]["count"] += 1
            new_rates.append(Rate(user_id=user_id, post_id=post_id, score=score, is_suspected=is_suspected))

    if updated_rates:
        Rate.objects.bulk_update(updated_rates, ['score', 'is_suspected'])

    if new_rates:
        Rate.objects.bulk_create(new_rates, ignore_conflicts=True)

    if new_scores:
        bulk_update_or_create_post_stats.delay(scores=new_scores)
