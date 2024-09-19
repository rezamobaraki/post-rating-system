from rest_framework.permissions import IsAuthenticated

from commons.viewsets import CreateModelViewSet
from posts.models import Rate
from posts.serialzers.rate import RateSerializer


class RateViewSet(CreateModelViewSet):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
