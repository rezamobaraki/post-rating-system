from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from commons.models import BaseModel
from posts.enums import RateScoreEnum


class Stat(BaseModel):
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name='rates', unique=True)
    average_rate = models.DecimalField(
        _("average rate"),
        null=True,
        validators=[
            MinValueValidator(RateScoreEnum.ZERO_STARS),
            MaxValueValidator(RateScoreEnum.FIVE_STARS)
        ]
    )
    count_rate = models.IntegerField(_("count rate"), default=0)

    class Meta:
        verbose_name = _('post rate stat')
        verbose_name_plural = _('post rate stats')
