from commons.viewsets import ListModelViewSet
from posts.models import Post
from posts.serialzers.post import PostSerializer


class PostViewSet(ListModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
