from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from commons.models import BaseModel
from posts.enums import RateScoreEnum

User = get_user_model()


class Rate(BaseModel):
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name='rates')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rates')
    score = models.IntegerField(
        null=True,
        validators=[
            MinValueValidator(RateScoreEnum.ZERO_STARS), MaxValueValidator(RateScoreEnum.FIVE_STARS)
        ]
    )

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.score}"
