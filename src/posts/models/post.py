from django.db import models
from django.utils.translation import gettext_lazy as _

from commons.models import BaseModel


class Post(BaseModel):
    title = models.CharField(_("title"), max_length=255)
    content = models.TextField(_("content"))

    class Meta:
        verbose_name = _('post')
        verbose_name_plural = _('posts')

    def __str__(self):
        return self.title

    @property
    def cache_key_average(self):
        return f"post_{self.id}_average_rate"

    @property
    def cache_key_count(self):
        return f"post_{self.id}_rate_count"
