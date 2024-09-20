from django.db import models
from django.utils.translation import gettext_lazy as _


class RateScoreEnum(models.IntegerChoices):
    ZERO_STARS = 0, _("Zero Stars")
    ONE_STAR = 1, _("One Star")
    TWO_STARS = 2, _("Two Stars")
    THREE_STARS = 3, _("Three Stars")
    FOUR_STARS = 4, _("Four Stars")
    FIVE_STARS = 5, _("Five Stars")

    def __str__(self):
        return self.label

    @classmethod
    def validate_choice(cls, value: str):
        if not any(value == choice.value for choice in cls):
            raise ValueError(f"Invalid choice: {value}. Valid choices are: {[choice.value for choice in cls]}")


class RateStatus(models.TextChoices):
    CREATED = 'rate created', _("Review Created")
    UPDATED = 'rate updated', _("Review Updated")

    def __str__(self):
        return self.label
