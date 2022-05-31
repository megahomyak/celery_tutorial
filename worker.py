from celery import Celery

app = Celery(
    "tasks", broker="pyamqp://testUser:testpassword@172.17.48.1//",
    backend="rpc://", include=["tasks"]
)
