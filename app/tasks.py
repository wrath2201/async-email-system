from app.celery_app import celery_app
import time

@celery_app.task(bind=True , autoretry_for=(),retry_kwargs={},retry_backoff=False) #marks function as a background job

def sample_task(self,name):
    print(f"processing job for {name}")

    #mark task as started
    self.update_state(state="STARTED")

    time.sleep(5)#simulate slow work
    
    print(f"job completed for {name}")
    return f"Hello {name}"