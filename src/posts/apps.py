from django.apps import AppConfig


class PostsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'posts'

    def ready(self):
        from posts.signals import update_post_stats_signal  # noqa
        from posts.signals import delete_post_stats_signal  # noqa
