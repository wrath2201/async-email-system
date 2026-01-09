
## 1. What the project does

This project is an **async email sending system** built with Flask, Celery, and Redis.
The API accepts a request to send an email, immediately returns a response, and offloads the actual email sending to a background worker. This prevents the API from blocking while waiting for SMTP operations.

The main goal of the project is to understand **asynchronous task processing**, **real-world deployment issues**, and the gap between **local development and production environments**.

This project focuses more on system behaviour and failure handling than on UI or feature
---

## 2. Why async was needed

Initially, email sending was done directly inside the Flask request cycle.
This caused the API to block until the SMTP server responded, which is slow and unreliable.

Problems with synchronous email sending:

* API response time depended on SMTP latency
* A failed SMTP login could crash the request
* Not scalable for multiple email requests

Solution:

* Move email sending to **Celery**
* Use **Redis** as a message broker
* Let Flask only enqueue tasks and return immediately

---

## 3. Local architecture

**Flask**

* Exposes an API endpoint
* Validates input
* Pushes email tasks to Redis via Celery

**Celery Worker**

* Listens to the Redis queue
* Executes the email sending logic
* Handles retries on failure

**Redis**

* Acts as the message broker
* Stores pending tasks until workers consume them

Flow:

```
Client → Flask API → Redis Queue → Celery Worker → SMTP Server
```

---

## 4. What worked locally

Locally, the system worked as expected:

* Flask successfully queued tasks
* Celery workers picked up tasks
* Emails were sent correctly via SMTP
* Environment variables were loaded properly using `.env`
* Redis was available without authentication issues


---

## 5. What broke during deployment

Several issues appeared only after moving to production:

* `requirements.txt` contained incorrect or unavailable package versions
* Redis was not configured or running properly on EC2
* Environment variables were missing or not loaded
* SMTP credentials failed due to incorrect env setup
* Permission and SSH-related confusion during server setup
* Difference between running services manually vs as background processes

---

## 6. How I fixed each issue

* Fixed `requirements.txt` by using valid package versions available on PyPI
* Installed and verified Redis manually on the EC2 instance
* Explicitly set environment variables instead of relying on `.env`
* Tested SMTP credentials independently before integrating
* Used system-level commands to confirm services were running
* Learned to debug by checking logs instead of guessing

---






