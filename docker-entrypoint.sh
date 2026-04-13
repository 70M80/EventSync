#!/bin/sh
set -e

echo "Starting application..."

exec gunicorn \
  -k uvicorn.workers.UvicornWorker \
  app.main:app \
  -w 1 \
  -b 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile - \
  --worker-tmp-dir /tmp \
  --log-level ${LOG_LEVEL:-info}