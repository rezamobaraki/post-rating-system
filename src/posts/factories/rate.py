import factory

from accounts.factories.user import UserFactory
from posts.enums import RateScoreEnum
from posts.factories.post import PostFactory
from posts.models.rate import Rate


class RateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rate

    post = factory.SubFactory(PostFactory)
    user = factory.SubFactory(UserFactory)
    rating = factory.Iterator(RateScoreEnum.values)
