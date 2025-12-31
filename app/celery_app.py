from celery import Celery

def make_celery():
    celery=Celery(
        "async_tasks",
        broker="redis://localhost:6379/0",## where job is done
        backend="redis://localhost:6379/0",##where results/status are stored , redis is doing both for now
        include=["app.tasks"]  # IMPORTANT
    )
    return celery
celery_app=make_celery()