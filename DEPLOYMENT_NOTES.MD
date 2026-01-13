
# DEPLOYMENT.md

**Async Email System – Production Deployment Guide**

This document explains **how this system is deployed on a Linux server** and **why each step exists**.
It is written so the project can be rebuilt from scratch without relying on memory.

---

## 1. Overview

This project is deployed as a **fully automated async backend system** using:

* Flask (API – producer)
* Celery (background worker – consumer)
* Redis (message broker)
* Gunicorn (production WSGI server)
* systemd (process manager)

Once deployed:

* No manual terminals are needed
* Services start on boot
* Services restart on crash

---

## 2. High-Level Architecture

```
Client
  ↓
Gunicorn (Flask API)        ← systemd
  ↓
Redis (Broker)
  ↓
Celery Worker               ← systemd
  ↓
SMTP Server
```

---

## 3. Server Requirements

* Ubuntu 22.04+ (tested on AWS EC2)
* Python 3.10+
* Redis

### Install system dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip redis-server
```

Verify Redis:

```bash
redis-cli ping
# Expected: PONG
```

---

## 4. Project Setup

### Clone repository

```bash
cd /home/ubuntu
git clone <REPO_URL> async-email-system
cd async-email-system
```

### Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 5. Environment Variables

Create `.env` in the project root:

```env
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
FLASK_DEBUG=0
```

Secure it:

```bash
chmod 600 .env
```

> `.env` is loaded by Flask and Celery at runtime.

---

## 6. Gunicorn (Production Server)

### Why Gunicorn

* Flask dev server is **not production-safe**
* Gunicorn handles:

  * concurrency
  * worker isolation
  * crash recovery

### Flask entry point

The Flask app lives at:

```
app/app.py
```

Gunicorn import path:

```
app.app:app
```

Manual test (one-time):

```bash
source venv/bin/activate
gunicorn app.app:app
```

---

## 7. systemd – Flask API Service

### Purpose

* Run Gunicorn in background
* Auto-restart on crash
* Auto-start on boot
* No SSH session required

### Service file

Create:

```bash
sudo nano /etc/systemd/system/async-email-api.service
```

```ini
[Unit]
Description=Async Email Flask API (Gunicorn)
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/async-email-system

Environment="PATH=/home/ubuntu/async-email-system/venv/bin"
ExecStart=/home/ubuntu/async-email-system/venv/bin/gunicorn \
          --workers 2 \
          --bind 127.0.0.1:8000 \
          app.app:app

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Enable and start

```bash
sudo systemctl daemon-reload
sudo systemctl start async-email-api
sudo systemctl enable async-email-api
```

### Verify

```bash
sudo systemctl status async-email-api
```

---

## 8. systemd – Celery Worker Service

### Purpose

* Process background jobs
* No manual `celery` command
* Auto-restart & auto-start

### Service file

Create:

```bash
sudo nano /etc/systemd/system/async-email-worker.service
```

```ini
[Unit]
Description=Async Email Celery Worker
After=network.target redis.service

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/async-email-system

Environment="PATH=/home/ubuntu/async-email-system/venv/bin"
ExecStart=/home/ubuntu/async-email-system/venv/bin/celery \
          -A app.celery_app worker --loglevel=info

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Enable and start

```bash
sudo systemctl daemon-reload
sudo systemctl start async-email-worker
sudo systemctl enable async-email-worker
```

### Verify

```bash
sudo systemctl status async-email-worker
```

---

## 9. End-to-End Test

Send a job request:

```bash
curl -X POST http://127.0.0.1:8000/start-job \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tushar",
    "email": "tusharsaini2201@gmail.com"
  }'
```

Expected:

* Immediate response with `job_id`
* Email delivered asynchronously

---

## 10. Logs & Debugging

### API logs (Gunicorn + Flask)

```bash
sudo journalctl -u async-email-api -f
```

### Worker logs (Celery)

```bash
sudo journalctl -u async-email-worker -f
```

These commands **do not start services** — they only display logs.

---

## 11. What systemd Automates

After deployment:

* No manual Flask start
* No manual Gunicorn start
* No manual Celery start
* No need for multiple terminals
* Services survive reboot and crashes

---








