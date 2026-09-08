from celery import Celery

from .config import get_settings

celery_app = Celery("sentinelscan", broker=get_settings().redis_url, backend=get_settings().redis_url, include=["app.tasks"])
celery_app.conf.update(task_track_started=True, task_serializer="json", accept_content=["json"], result_serializer="json")
