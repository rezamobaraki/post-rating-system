from django.db.models import Avg, Count
from django.db.models.functions import Coalesce, Round

from posts.models.post import Post
from posts.models.rate import Rate


def rates_average(*, post: Post) -> float:
    return Rate.objects.filter(post=post).aggregate(
        average=Coalesce(Round(Avg('score'), precision=1), 0.0)
    )['average']


def rates_count(*, post: Post) -> int:
    return Rate.objects.filter(post=post).aggregate(count=Count('id'))['count']
