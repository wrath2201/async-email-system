# Flask API that acts as a producer:
# accepts HTTP requests and enqueues Celery background jobs
from flask import Flask , jsonify , request

from celery.result import AsyncResult
from app.celery_app import celery_app

# Import Celery task (must match worker import path exactly)
from app.tasks import sample_task

app=Flask(__name__)

@app.route("/start-job",methods=["POST"])

def start_job():
    data=request.get_json()
    name=data.get("name","User")

    # Queue this task for background execution:
    # `.delay()` does NOT call the function here — it serializes the task + args,
    # sends them to the broker (Redis), and returns immediately with a task ID.

    job=sample_task.delay(name)

    return jsonify({
        "job_id":job.id,
        "status":"PENDING"
    })

@app.route("/job-status/<job_id>",methods=["GET"])
def job_status(job_id):
    #query task state from redis backened only

    result=AsyncResult(job_id,app=celery_app)
    response={
        "job_id":job_id,
        "state": result.state
    }
    if result.successful():
        response["result"]=str(result.result)

    if result.failed():
        response["error"]=str(result.result)

    return jsonify(response)

if __name__ =="__main__":
    app.run(debug=True)