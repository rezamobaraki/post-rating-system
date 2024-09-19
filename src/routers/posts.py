from django.urls import include, path

app_name = 'posts'

urlpatterns = [
    path('', include('posts.urls.post', namespace='post'), name='posts'),
    path('<int:post_id>/rates/', include('posts.urls.rate', namespace='rate'), name='rates'),
]
