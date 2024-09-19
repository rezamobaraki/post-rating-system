from django.contrib.auth import get_user_model

from posts.enums import RateScoreEnum
from posts.models.post import Post
from posts.models.rate import Rate

User = get_user_model()


# TODO: check to change to aupdate_or_create
def update_or_create_rate(*, user: User, post: Post, score: RateScoreEnum) -> tuple[Rate, bool]:
    rate, created = Rate.objects.update_or_create(
        user=user, post=post,
        defaults={'score': score}
    )
    return rate, created
