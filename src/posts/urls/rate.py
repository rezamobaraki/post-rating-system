from rest_framework.routers import SimpleRouter

from posts.viewsets import RateViewSet

app_name = 'rate'

router = SimpleRouter()

router.register(r'', RateViewSet, basename='rate')

urlpatterns = router.urls
