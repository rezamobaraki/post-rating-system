from django.db.models.signals import post_save
from django.dispatch import receiver

from posts.models import Rate


@receiver(post_save, sender=Rate)
def update_post_stats_signal(sender, instance, **kwargs):
    from posts.services.commands import update_or_create_stat
    update_or_create_stat(post_id=instance.post.id, new_score=instance.score)


@receiver(post_save, sender=Rate)
def delete_post_stats_signal(sender, instance, **kwargs):
    from django.core.cache import cache
    from core.settings.third_parties.redis_templates import RedisKeyTemplates
    from posts.models import PostStat
    PostStat.objects.filter(post_id=instance.post.id).delete()
    key = RedisKeyTemplates.format_post_stats_key(post_id=instance.post.id)
    cache.delete(key)
