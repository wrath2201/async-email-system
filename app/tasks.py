from app.celery_app import celery_app
import time
import redis
from pathlib import Path
import os

redis_client=redis.Redis(host="localhost",port=6379,db=1)
OUTPUT_DIR=Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# Automatic retry configuration:
# - Retries only on ValueError
# - Max 3 retries with exponential backoff
# - Same task ID is reused across retries
@celery_app.task(
        bind=True ,
        autoretry_for=(ValueError,),
        retry_kwargs={"max_retries":3},
        retry_backoff=5,
        time_limit=3,   #hard limit( seconds )
        ) #marks function as a background job

def sample_task(self,name):

    task_id=self.request.id
    output_file=OUTPUT_DIR / f"{task_id}.txt"

    #idempotency check
    # Idempotency guard:
    # Ensures retries do not repeat side effects (e.g., duplicate emails)

    if redis_client.exists(task_id):
        print(f"Task{task_id} already processed . Skipping")
        return "Already processed"
    

    print(f"processing job for {name}")
    # Time limit protects workers from tasks that hang indefinitely

    if name=="crash":
        print("simulating worker crash")
        os._exit(1) # force kill the worker process

    if name=="slow":
        time.sleep(10) # deliberately exceeds time_limit
    time.sleep(2)

    # INTENTIONAL FAILURE for learning
    if name == "fail":
        raise ValueError("Simulated task failure")
    
    # REAL SIDE EFFECT 
    output_file.write_text(f"Hello {name}\n")

    
    #Mark task as completed
    redis_client.set(task_id,"done")


    print(f"job completed for {name}")
    return f"Hello {name}"