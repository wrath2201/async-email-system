from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

def make_celery():
    celery=Celery(
        "async_tasks",
        broker=os.getenv("REDIS_BROKER_URL"), ## where job is queued
        backend=os.getenv("REDIS_BACKEND_URL"),##where results/status are stored , redis is doing both for now
        include=["app.tasks"],  # IMPORTANT
    )
    return celery
celery_app=make_celery()