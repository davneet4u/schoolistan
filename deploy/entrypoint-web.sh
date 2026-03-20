#!/usr/bin/env bash
set -euo pipefail

: "${WEB_CONCURRENCY:?WEB_CONCURRENCY is required}"

cd /app

exec gunicorn teachothers.wsgi \
  --workers "${WEB_CONCURRENCY}" \
  --threads 2 \
  --bind 0.0.0.0:8000 \
  --log-file - \
  --access-logfile - \
  --access-logformat '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%({Referer}i)s" "%({User-Agent}i)s"'
