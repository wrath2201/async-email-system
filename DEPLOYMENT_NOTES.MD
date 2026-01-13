
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
* Nginx (reverse proxy)
* systemd (process manager)

Once deployed:

* No manual terminals are needed
* Services start on boot
* Services restart on crash
* Only Nginx is exposed to the internet

---

## 2. High-Level Architecture

```
Client
  ↓
Nginx (port 80)
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
* Nginx

### Install system dependencies

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip redis-server nginx
```

Verify Redis:

```bash
redis-cli ping
# Expected: PONG
```

Verify Nginx:

```bash
sudo systemctl status nginx
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

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl start async-email-api
sudo systemctl enable async-email-api
```

---

## 8. systemd – Celery Worker Service

### Purpose

* Process background jobs
* No manual `celery` command
* Auto-restart & auto-start

### Service file

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

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl start async-email-worker
sudo systemctl enable async-email-worker
```

---

## 9. Nginx – Reverse Proxy

### Why Nginx is used

* Acts as the **public entry point**
* Listens on standard HTTP port (80)
* Forwards requests internally to Gunicorn
* Keeps Gunicorn private and inaccessible from the internet

### Nginx configuration

Disable default site:

```bash
sudo rm /etc/nginx/sites-enabled/default
```

Create config file:

```bash
sudo nano /etc/nginx/sites-available/async-email
```

```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/async-email /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 10. End-to-End Test (Production)

Send request **from outside the server**:

```bash
curl -X POST http://<EC2_PUBLIC_IP>/start-job \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tushar",
    "email": "tusharsaini2201@gmail.com"
  }'
```

Expected:

* Immediate response with `job_id`
* Email delivered asynchronously

> Note: Port 8000 is not exposed publicly; all traffic goes through Nginx on port 80.

---

## 11. Logs & Debugging

### API logs (Gunicorn + Flask)

```bash
sudo journalctl -u async-email-api -f
```

### Worker logs (Celery)

```bash
sudo journalctl -u async-email-worker -f
```

---

## 12. Security Group (Inbound Rules) – Explained

AWS Security Groups act as a network-level firewall.
Inbound rules determine which incoming network packets are allowed to reach the EC2 instance.

These rules are enforced **before** traffic reaches the Linux OS, Nginx, or the application.

### Final Inbound Rules

| Port | Protocol | Source      | Purpose                      |
| ---- | -------- | ----------- | ---------------------------- |
| 22   | TCP      | My IP (/32) | Secure SSH access            |
| 80   | TCP      | 0.0.0.0/0   | Public HTTP access via Nginx |

### Why TCP is used

* HTTP and SSH are TCP-based protocols
* TCP provides reliable, ordered, connection-oriented communication
* UDP is unsuitable for APIs and remote login

### Why port 80 is public

* Nginx is the public-facing reverse proxy
* It forwards requests internally to Gunicorn
* Gunicorn listens only on 127.0.0.1 and is not exposed

### Why other ports are blocked

* Port 8000 (Gunicorn): internal application server
* Port 5000 (Flask dev server): development only
* Redis and Celery are internal services

Blocking these ports enforces the **principle of least privilege**.

---

## 13. Local vs Production Execution

**Local Development**

* Flask dev server
* Celery started manually
* No Nginx
* No systemd

**Production**

* Gunicorn + systemd
* Celery worker + systemd
* Nginx reverse proxy
* Network-level firewall via Security Groups

---

## 14. Summary

This deployment separates:

* **public access (Nginx)**
* **application logic (Gunicorn + Flask)**
* **background processing (Celery + Redis)**

All services are automated, isolated, and restart-safe.

---







