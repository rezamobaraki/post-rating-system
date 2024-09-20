import os

from celery import Celery
from celery.schedules import crontab

from core.env import env

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.django.local')

host = env.str("REDIS_HOST", default="localhost")
port = env.int("REDIS_PORT", default=6379)
password = env.str("REDIS_PASSWORD", default=None)
celery_db = env.int("REDIS_CELERY_DB", default=1)
if password:
    redis_url = f"redis://:{password}@{host}:{port}/{celery_db}"  # noqa
else:
    redis_url = f"redis://{host}:{port}/{celery_db}"  # noqa

celery_app = Celery('apprx', broker=redis_url)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
celery_app.config_from_object('django.conf:settings', namespace='CELERY')

# Load scheduled tasks.
celery_app.conf.beat_schedule = {
    'sync_posts_stat': {
        'task': 'posts.tasks.update_post_stats_periodical',
        'schedule': crontab(day_of_week="*", hour=7, minute=00),
        'args': ('day',)
    },
}

# Load task modules from all registered Django apps.
celery_app.autodiscover_tasks()
