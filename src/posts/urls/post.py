from rest_framework.routers import SimpleRouter

from posts.viewsets import PostViewSet

app_name = 'post'

router = SimpleRouter()

router.register(r'', PostViewSet, basename='post')

urlpatterns = router.urls
