from __future__ import absolute_import, unicode_literals
import os
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "websocket_project.settings")

app = Celery("websocket_project")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

# new config for fetch result from mongo
app.conf.update(
    broker_url="redis://localhost:6379/0",
    result_backend="mongodb://localhost:27017/celery_results",
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
# =======================================


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
