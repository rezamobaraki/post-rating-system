from commons.pagination import StandardResultsSetPagination
from commons.viewsets import ListModelViewSet
from posts.models import Post
from posts.serialzers.post import PostSerializer


class PostViewSet(ListModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return self.queryset.prefetch_related('stat')
