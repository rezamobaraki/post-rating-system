from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from commons.viewsets import CreateModelViewSet
from posts.models import Post, Rate
from posts.serialzers.rate import RateSerializer


class RateViewSet(CreateModelViewSet):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        serializer.save(post=post)
