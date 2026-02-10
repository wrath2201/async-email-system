import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '30s', target: 5 },
    { duration: '30s', target: 10 },
    { duration: '30s', target: 20 },
    { duration: '30s', target: 60 },
  ],
};

export default function () {
  const url = 'http://localhost:5000/send-email';

  const payload = JSON.stringify({
    to: 'test@example.com',
    subject: 'Load Test',
    body: 'Testing async email system'
  });

  const params = {
    headers: { 'Content-Type': 'application/json' },
  };

  const res = http.post(url, payload, params);

  check(res, {
    'status is not 5xx': (r) => r.status < 500,
  });

  sleep(0.1);
}
