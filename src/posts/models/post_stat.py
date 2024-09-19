from django.db import models
from django.utils.translation import gettext_lazy as _

from commons.models import BaseModel
from posts.models import Post


class PostStat(BaseModel):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='stat')
    average_rate = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_rates = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('post rate stat')
        verbose_name_plural = _('post rate stats')
