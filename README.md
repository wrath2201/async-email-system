# Async Email System (Celery + Redis + Flask)

A simple asynchronous job processing system built that demonstrate how to offload long-running tasks from a Flask API into Celery workers using Redis.

## Problem Statement

Synchronous APIs block while performing long-running tasks such as sending emails or processing data.  
This leads to slow responses, poor scalability, and fragile systems.

This project solves that problem by:
- Accepting requests quickly via an API
- Queuing background jobs
- Processing them asynchronously using workers

## Features
- Non-blocking job submission via REST API
- Background task execution using Celery workers
- Redis used as:
    - message broker (task queue)
    - result backend (task state & result storage)
- Job status tracking using task IDs
-Controlled retries with exponential backoff
-Basic idempotency guard to prevent duplicate task side effects

## Tech Stack
- Python
- Flask (API/job producer)
- Celery( background task processing)
- Redis (broker and result backened)

## Architecture Flow
Client → Flask API (producer) → Redis (Broker) → Celery Worker(consumer) → Redis (Result Backend)

- The Flask API never executes long-running tasks
- Tasks are queued in Redis
- Celery workers pull tasks and execute them independently
- Task state and results are stored in Redis


## API Endpoints

### Start Job

**POST** `/start-job`

**Request Body**
```json
{
  "name": "User"
}



### response
{
  "job_id": "<task_id>",
  "status": "PENDING"
}





---

### Job Status

```md
### Job Status

**GET** `/job-status/<job_id>`

**Response (Success)**
```json
{
  "job_id": "<task_id>",
  "state": "SUCCESS",
  "result": "Hello User"
}

Response (Failure)
{
  "job_id": "<task_id>",
  "state": "FAILURE",
  "error": "Simulated task failure"
}




---

# STEP 7 — How to Run Locally

### Why this matters
Without this, repo feels incomplete.

### Add

```md
## Run Locally

### 1. Start Redis
```bash
redis-server


```md
### 3. Start Flask API
```bash
python -m app.app



---

# STEP 8 — Important Notes (engineering maturity)

### Why this matters
Shows awareness of limitations.

### Add

```md
## Notes

- Task results stored in Redis are intended for short-lived inspection only
- In production systems, result backends and idempotency strategies may differ
- This project focuses on correctness and architecture rather than UI
