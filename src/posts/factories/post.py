import factory

from posts.models.post import Post


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    title = factory.Faker('sentence', nb_words=4)
    summary = factory.Faker('paragraph', nb_sentences=3)
