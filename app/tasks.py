from app.celery_app import celery_app
import time
import redis

redis_client=redis.Redis(host="localhost",port=6379,db=1)

# Automatic retry configuration:
# - Retries only on ValueError
# - Max 3 retries with exponential backoff
# - Same task ID is reused across retries
@celery_app.task(bind=True , autoretry_for=(ValueError,),retry_kwargs={"max_retries":3},retry_backoff=5,) #marks function as a background job

def sample_task(self,name):

    task_id=self.request.id

    #idempotency check
    # Idempotency guard:
    # Ensures retries do not repeat side effects (e.g., duplicate emails)

    if redis_client.exists(task_id):
        print(f"Task{task_id} already processed . Skipping")
        return "Already processed"
    

    print(f"processing job for {name}")
    time.sleep(2)

    # INTENTIONAL FAILURE for learning
    if name == "fail":
        raise ValueError("Simulated task failure")
    
    #Mark task as completed
    redis_client.set(task_id,"done")


    print(f"job completed for {name}")
    return f"Hello {name}"