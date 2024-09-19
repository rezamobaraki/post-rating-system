from django.db.models.signals import post_save
from django.dispatch import receiver

from posts.models import Rate


@receiver(post_save, sender=Rate)
def update_post_stats(sender, instance, **kwargs):
    from posts.services.commands.stat import get_or_create_stat
    get_or_create_stat(post=instance.post, rate=instance)
