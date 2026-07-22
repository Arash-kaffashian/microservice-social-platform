from celery import Celery
from decouple import config


""" Celery setting """


# Host and Port config
HOST = config("HOST")
PORT = config("PORT")

# redis config
celery = Celery(
    "email_service",
    broker=f"redis://{HOST}:{PORT}/0",
)

# data type config
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
)

# tasks setting
celery.conf.imports = (
    "app.tasks.system_email",
)
