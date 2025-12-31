# Async Email System (Celery + Redis + Flask)

A simple asynchronous job processing system built using Flask, Celery, and Redis.

## Features
- Non-blocking job submission via REST API
- Background task execution using Celery workers
- Redis as message broker and result backend
- Job status tracking using task IDs

## Tech Stack
- Python
- Flask
- Celery
- Redis

## Architecture Flow
Client → Flask API → Redis (Broker) → Celery Worker → Redis (Result Backend)

## API Endpoints

### Start Job
POST /start-job  
Body:
```json
{ "name": "User" }


### response
{
  "job_id": "<task_id>",
  "status": "PENDING"
}




Job Status

GET /job-status/<job_id>

Response:

{
  "job_id": "<task_id>",
  "state": "SUCCESS",
  "result": "Hello User"
}



Run Locally
Start Redis
redis-server

Start Worker
celery -A app.celery_app worker --loglevel=info

Start API
python -m app.app