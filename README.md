
# Async Email System (Flask + Celery + Redis)

An asynchronous job processing system that demonstrates how to offload long-running or side-effect-heavy tasks from a Flask API into Celery workers using Redis.

---

## Problem Statement

Synchronous APIs block while performing long-running tasks such as sending emails or processing data.  
This leads to slow responses, poor scalability, and fragile systems.

This project solves that problem by:
- Accepting requests quickly via an API
- Queuing background jobs
- Processing them asynchronously using workers

---

## Features

- Non-blocking job submission via REST API
- Background task execution using Celery workers
- Redis used as:
  - Message broker (task queue)
  - Result backend (task state & result storage)
- Job status tracking using task IDs
- Controlled retries with exponential backoff
- Basic idempotency guard to prevent duplicate task side effects
- Real side-effect simulation (SMTP email / file write)

---

## Tech Stack

- Python  
- Flask — API / job producer  
- Celery — background task processing  
- Redis — broker, result backend, and idempotency store  

---

## Architecture Overview

```

Client
↓
Flask API (Producer)
↓
Redis (Broker / Queue)
↓
Celery Worker (Consumer)
↓
Redis (Result Backend)

````

- The Flask API never executes long-running tasks
- Tasks are queued in Redis
- Celery workers pull tasks and execute them independently
- Task state and results are stored in Redis

---

## API Endpoints

### Start Job

**POST** `/start-job`

**Request Body**
```json
{
  "name": "User"
}
````

**Response**

```json
{
  "job_id": "<task_id>",
  "status": "PENDING"
}
```

---

### Job Status

**GET** `/job-status/<job_id>`

**Response (Success)**

```json
{
  "job_id": "<task_id>",
  "state": "SUCCESS",
  "result": "Hello User"
}
```

**Response (Failure)**

```json
{
  "job_id": "<task_id>",
  "state": "FAILURE",
  "error": "Simulated task failure"
}
```

* Reads task state from Redis
* Does not trigger task execution

---

## Task Behavior

* Tasks execute asynchronously in Celery workers, not in the Flask API
* Failures are isolated to individual tasks and do not crash the system
* Retries are applied only for recoverable errors
* Idempotency guards ensure retries do not repeat side effects
* Tasks may be re-executed after crashes (at-least-once delivery)

---

## Observability & System Visibility

This system is designed to be observable without relying on heavy monitoring tools.

* Task state stored in Redis is the **source of truth** for task progress
* Clients can track task lifecycle using task IDs via the status API
* Logs are used for debugging, not for determining system state
* Worker crashes are detected via task re-delivery semantics

---

## Run Locally

### 1. Start Redis

```bash
redis-server
```

### 2. Start Celery Worker

```bash
celery -A app.celery_app worker --loglevel=info
```

### 3. Start Flask API

```bash
python -m app.app
```

---

## Notes

* Task results stored in Redis are intended for short-lived inspection only
* Redis is used for learning purposes as both broker and backend
* Real side effects must be protected by idempotency to avoid duplication during retries
* This project focuses on correctness and architecture rather than UI or deployment

```

