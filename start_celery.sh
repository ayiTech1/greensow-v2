#!/bin/bash

echo "Starting Celery worker with solo pool..."
celery -A core worker --concurrency=1 --pool=solo --loglevel=info
