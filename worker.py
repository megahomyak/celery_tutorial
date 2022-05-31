from celery import Celery

import celery_configuration

app = Celery(
    "tasks", broker="pyamqp://testUser:testpassword@172.17.48.1//",
    backend="rpc://", config_source=celery_configuration, include=["tasks"]
)
